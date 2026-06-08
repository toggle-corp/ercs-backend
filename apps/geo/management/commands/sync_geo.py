"""Sync Ethiopia administrative areas (levels 0–2) from the IFRC GO API.

Usage
-----
    ./manage.py sync_geo
    ./manage.py sync_geo --dry-run   # fetch and log, but roll back DB writes

What it does
------------
Upserts AdminArea rows for country (COUNTRY), region (REGION), and zone (ZONE)
by calling three IFRC GO REST endpoints. Records are keyed on ifrc_id so the
command is safe to re-run — existing rows are updated in place, new rows are
inserted.

Woreda (WOREDA) level is not available from IFRC GO and must be seeded separately.
"""

import typing
from collections.abc import Iterator
from typing import Any

import requests
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.geo.models import AdminArea, AdminAreaLevel

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

COUNTRY_IFRC_ID = 65  # Ethiopia
COUNTRY_ISO3 = "ETH"
COUNTRY_PCODE = "ET"

GO_DOMAIN = "https://goadmin.ifrc.org"
HTTP_TIMEOUT = 30.0


# ---------------------------------------------------------------------------
# Management command
# ---------------------------------------------------------------------------


class Command(BaseCommand):
    """Sync Ethiopia administrative areas (levels 0–2) from IFRC GO."""

    @typing.override
    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Fetch data and log what would happen, but roll back all DB writes.",
        )

    @typing.override
    def handle(self, *args: Any, **options: Any) -> None:
        dry_run: bool = options["dry_run"]
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run mode — changes will be rolled back."))

        syncer = GeoSyncer(stdout=self.stdout, style=self.style)
        syncer.run(dry_run=dry_run)


# ---------------------------------------------------------------------------
# Syncer
# ---------------------------------------------------------------------------


class GeoSyncer:
    def __init__(self, stdout: Any, style: Any) -> None:
        self.stdout = stdout
        self.style = style
        self._counts: dict[AdminAreaLevel, dict[str, int]] = {
            AdminAreaLevel.COUNTRY: {"created": 0, "updated": 0},
            AdminAreaLevel.REGION: {"created": 0, "updated": 0},
            AdminAreaLevel.ZONE: {"created": 0, "updated": 0},
        }

    def run(self, dry_run: bool = False) -> None:
        with transaction.atomic():
            self.sync_country()
            self.sync_regions()
            self.sync_zones()

            self._print_summary()

            if dry_run:
                transaction.set_rollback(True)
                self.stdout.write(self.style.WARNING("Dry run complete — transaction rolled back."))

    # ------------------------------------------------------------------
    # Level sync methods
    # ------------------------------------------------------------------

    def sync_country(self) -> AdminArea:
        url = f"{GO_DOMAIN}/api/v2/country/{COUNTRY_IFRC_ID}/"
        self.stdout.write(f"Fetching country from {url}")

        resp = requests.get(url, timeout=HTTP_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        centroid_lat, centroid_lon = self._extract_centroid(data.get("bbox"))

        area, created = AdminArea.objects.update_or_create(
            ifrc_id=COUNTRY_IFRC_ID,
            defaults={
                "pcode": COUNTRY_PCODE,
                "name": data["name"],
                "level": AdminAreaLevel.COUNTRY,
                "parent": None,
                "geo_shape": data.get("bbox") or None,
                "centroid_lat": centroid_lat,
                "centroid_lon": centroid_lon,
            },
        )
        self._log(area, created)
        self._counts[AdminAreaLevel.COUNTRY]["created" if created else "updated"] += 1
        return area

    def sync_regions(self) -> list[AdminArea]:
        url = f"{GO_DOMAIN}/api/v2/district/?country={COUNTRY_IFRC_ID}"
        country = AdminArea.objects.get(ifrc_id=COUNTRY_IFRC_ID)
        areas: list[AdminArea] = []

        for record in self._paginate(url):
            ifrc_id: int = record["id"]
            pcode: str | None = record.get("code") or None
            centroid_lat, centroid_lon = self._extract_centroid(record.get("bbox"))

            area, created = AdminArea.objects.update_or_create(
                ifrc_id=ifrc_id,
                defaults={
                    "pcode": pcode,
                    "name": record["name"],
                    "level": AdminAreaLevel.REGION,
                    "parent": country,
                    "geo_shape": record.get("bbox") or None,
                    "centroid_lat": centroid_lat,
                    "centroid_lon": centroid_lon,
                },
            )
            self._log(area, created)
            self._counts[AdminAreaLevel.REGION]["created" if created else "updated"] += 1
            areas.append(area)

        return areas

    def sync_zones(self) -> list[AdminArea]:
        url = f"{GO_DOMAIN}/api/v2/admin2/?admin1__country={COUNTRY_IFRC_ID}"
        regions_by_ifrc_id = {
            a.ifrc_id: a for a in AdminArea.objects.filter(level=AdminAreaLevel.REGION) if a.ifrc_id is not None
        }
        areas: list[AdminArea] = []

        for record in self._paginate(url):
            ifrc_id: int = record["id"]
            pcode: str | None = record.get("code") or None
            parent_ifrc_id: int = record["district_id"]

            parent = regions_by_ifrc_id.get(parent_ifrc_id)
            if parent is None:
                raise ValueError(
                    f"Zone {pcode!r} (ifrc_id={ifrc_id}) references unknown "
                    f"parent district_id={parent_ifrc_id}. Ensure regions were synced first.",
                )

            centroid_lat, centroid_lon = self._extract_centroid_from_geojson(record.get("centroid"))
            if centroid_lat is None:
                centroid_lat, centroid_lon = self._extract_centroid(record.get("bbox"))

            area, created = AdminArea.objects.update_or_create(
                ifrc_id=ifrc_id,
                defaults={
                    "pcode": pcode,
                    "name": record["name"],
                    "level": AdminAreaLevel.ZONE,
                    "parent": parent,
                    "geo_shape": record.get("bbox") or None,
                    "centroid_lat": centroid_lat,
                    "centroid_lon": centroid_lon,
                },
            )
            self._log(area, created)
            self._counts[AdminAreaLevel.ZONE]["created" if created else "updated"] += 1
            areas.append(area)

        return areas

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _paginate(self, url: str) -> Iterator[dict[str, Any]]:
        """Follow IFRC GO pagination until next is null."""
        next_url: str | None = url
        while next_url:
            resp = requests.get(next_url, timeout=HTTP_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            yield from data["results"]
            next_url = data.get("next")

    def _extract_centroid(self, bbox: dict[str, Any] | None) -> tuple[float | None, float | None]:
        """Derive lat/lon centroid from a GeoJSON Polygon bbox."""
        if not bbox:
            return None, None
        try:
            coords = bbox["coordinates"][0]  # exterior ring
            lons = [c[0] for c in coords]
            lats = [c[1] for c in coords]
            return (min(lats) + max(lats)) / 2, (min(lons) + max(lons)) / 2
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f"  Could not derive centroid from bbox: {exc}"))
            return None, None

    def _extract_centroid_from_geojson(self, centroid: dict[str, Any] | None) -> tuple[float | None, float | None]:
        """Extract lat/lon from a GeoJSON Point centroid."""
        if not centroid:
            return None, None
        try:
            lon, lat = centroid["coordinates"]
            return float(lat), float(lon)
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f"  Could not parse centroid: {exc}"))
            return None, None

    def _log(self, area: AdminArea, created: bool) -> None:
        verb = "Created" if created else "Updated"
        level_label = area.get_level_display()  # type: ignore[reportAttributeAccessIssue]
        self.stdout.write(f"  {verb} {level_label} {area.pcode or '(no pcode)':15s} {area.name}")

    def _print_summary(self) -> None:
        self.stdout.write(self.style.SUCCESS("\nSync complete:"))
        level_names = {
            AdminAreaLevel.COUNTRY: "Country",
            AdminAreaLevel.REGION: "Region",
            AdminAreaLevel.ZONE: "Zone",
        }
        for level, counts in self._counts.items():
            self.stdout.write(
                self.style.SUCCESS(
                    f"  {level_names[level]}: {counts['created']} created, {counts['updated']} updated",
                ),
            )
