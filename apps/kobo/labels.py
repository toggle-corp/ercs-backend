"""Resolve Kobo choice *codes* to human labels using a stored form schema.

Kobo submissions record choice values as codes (``Modality2``,
``vulnerable2_vulnerable-groups``, ``assessment_ercs``, branch ``RE-008``). The
display labels live in the asset's ``content`` — ``choices`` maps
``(list_name, code) -> label`` and ``survey`` says which list a field draws from.

The sync precomputes two compact maps (:func:`build_label_maps`) and stores them
on :class:`~apps.kobo.models.KoboFormSchema`; :class:`FormLabels` loads them and
translates values at request time. XLSForm requires question names to be unique
within a form, so a raw key's leaf (``group/leaf`` -> ``leaf``) is enough to find
the field's choice list.
"""

from dataclasses import dataclass
from typing import Any

from apps.kobo.models import KoboForm, KoboFormSchema


def _label_text(label: Any) -> str | None:
    """Kobo labels are usually ``["English", None]`` (translations), sometimes a bare string."""
    if isinstance(label, list):
        return next((str(item) for item in label if item), None)
    return str(label) if label else None


def build_label_maps(content: dict[str, Any]) -> dict[str, Any]:
    """Precompute ``{"choices": {list: {code: label}}, "fields": {leaf: {list, multiple}}}``."""
    choices: dict[str, dict[str, str]] = {}
    for row in content.get("choices", []):
        list_name = row.get("list_name")
        code = row.get("name")
        if not list_name or code is None:
            continue
        choices.setdefault(str(list_name), {})[str(code)] = _label_text(row.get("label")) or str(code)

    fields: dict[str, dict[str, Any]] = {}
    for row in content.get("survey", []):
        rtype = str(row.get("type") or "")
        leaf = row.get("name")
        if not leaf or not rtype.startswith("select_"):
            continue
        list_name = row.get("select_from_list_name")
        if not list_name:
            # Older forms encode the list in the type string: "select_one <list>".
            parts = rtype.split()
            list_name = parts[1] if len(parts) == 2 else None
        if not list_name:
            continue
        fields[str(leaf)] = {"list": str(list_name), "multiple": rtype.startswith("select_multiple")}

    return {"choices": choices, "fields": fields}


@dataclass
class FormLabels:
    """Loaded code->label maps for one form, with resolution helpers."""

    choices: dict[str, dict[str, str]]
    fields: dict[str, dict[str, Any]]

    @classmethod
    def load(cls, form: KoboForm) -> "FormLabels":
        schema = KoboFormSchema.objects.filter(form=form).first()
        labels = (schema.labels if schema else None) or {}
        return cls(choices=labels.get("choices", {}), fields=labels.get("fields", {}))

    @staticmethod
    def _humanize(code: str) -> str:
        return code.replace("_", " ").strip()

    def resolve_many(self, field_key: str, value: str | None) -> list[str]:
        """Resolve a raw value to labels. A ``select_multiple`` value is space-delimited.

        Unknown codes fall back to a humanized version rather than being dropped.
        """
        if not value:
            return []
        leaf = field_key.rsplit("/", 1)[-1]
        spec = self.fields.get(leaf)
        codes = value.split() if (spec and spec.get("multiple")) else [value]
        table = self.choices.get(spec["list"], {}) if spec else {}
        return [table.get(code) or self._humanize(code) for code in codes if code]

    def resolve_one(self, field_key: str, value: str | None) -> str | None:
        labels = self.resolve_many(field_key, value)
        return labels[0] if labels else None

    def collect(self, raw: dict[str, Any], keys: list[str]) -> list[str]:
        """Resolve several fields (e.g. ``sector1/2/3``) into one de-duplicated chip list."""
        out: list[str] = []
        for key in keys:
            for label in self.resolve_many(key, raw.get(key)):
                if label and label not in out:
                    out.append(label)
        return out
