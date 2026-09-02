# ERCS Kobo Toolkit — API & Data Reference

> Generated 2026-08-27 from live schema + data pulls. Country scope: **Ethiopia (ETH)**.
> Owner Kobo account: **`ercseoc2019`**. Base host: **`https://kobo.ifrc.org`**.

## 1. How the API works

KoboToolbox **v2 REST API** (Django REST Framework). Use `/api/v2/` — the old bare
`/assets/` (v1) endpoint now returns `410 Gone`.

**Auth** — token in a request header:

```
Authorization: Token <KEY>
```

- **Form schema is public** (`GET /api/v2/assets/<uid>/`), **submission data is private**
  (`/data/` returns `404 Not found` without a valid, authorised token).
- We hold **two tokens** (in `.env`):
  - `KOBO_ACCESS_TOKEN` ("new") — grants Alert, RNA, Field.
  - `KOBO_OLD_TOKEN` ("old") — grants **all four**, including Response Reporting
    (the new token `404`s on Response Reporting).

**Response shape** — DRF pagination:

```json
{ "count": 127, "next": "…?start=1000", "previous": null, "results": [ {…} ] }
```

**Useful query params on `/data/`:**

| Param | Example | Purpose |
|---|---|---|
| `format` | `format=json` | JSON output |
| `limit` / `start` | `limit=1000&start=0` | page size / offset (or follow `next`) |
| `query` | `query={"_submission_time":{"$gt":"2026-08-01T00:00:00"}}` | server-side Mongo filter → **incremental sync** |
| `sort` | `sort={"_submission_time":-1}` | order (newest first) |
| `fields` | `fields=["_id","context/hazard"]` | projection |

## 2. Data endpoints

| Form | Asset UID | `/data/` count | Token to use |
|---|---|---|---|
| Emergency Alert | `aydYC8AYCDuX7y4PwfvgrX` | 127 | new or old |
| Rapid Needs Assessment (RNA) | `aPuV7tDb9mdRiK8hUhkxJC` | 181 | new or old |
| Emergency Field | `aby6sxp4DyEiohs4XMn7Mu` | 85 | new or old |
| Response Reporting (monthly M&E) | `a8k4JQNvj4bcrr8yt7zhTa` | 431 | **old only** |

Endpoint template:

```
GET https://kobo.ifrc.org/api/v2/assets/<uid>/data/?format=json
```

### System fields (present on every record)

`_id` (stable int submission id — **use as upsert key**), `_uuid`, `meta/instanceID`,
`_submission_time` (UTC), `_submitted_by` (Kobo username or `null`), `_geolocation` `[lat,lon]`,
`_attachments[]` (each has an auth-gated `download_url`), `_validation_status`,
`_xform_id_string`, `__version__`, `_status`.

### How the forms link together

- Alert emits **`emergency_code/unique_code`** (e.g. `EM-20260815-Wind storm-Tigray-zone`).
- RNA carries it as **`context/emergency-selection`** / `location/alert_code`.
- Field carries it as **`context/emergency-selection`** / `location/alert_code`.
- Response Reporting is **standalone** — keyed by `report_month`, not the emergency code.

### Gotchas

- **Values are strings**, incl. numbers (`"41836"`) — cast on ingest.
- Response Reporting has three questions all named `disability`; Kobo disambiguates them as
  **`disability` / `disability_001` / `disability_002`** (Total / Female / Male).
- `select_multiple` values are **space-delimited** in one string
  (e.g. `zone-multiple: "Central Eastern North_Western"`).
- `geopoint` is a 4-token string `"lat lon alt acc"`; `_geolocation` gives the parsed `[lat,lon]`.
- **PII**: `context/prepared_by` (name) and `context/phone` are present — phones are **masked** in the examples below.

## 3. Data examples

### 3.1 Emergency Alert — full record

```json
{
  "_id": 14794651,
  "formhub/uuid": "b4844869d001428096b55af5a6743ca4",
  "context/date_of_reported": "2026-08-24T15:12:00.000+03:00",
  "context/prepared_by": "Kidu Gebremedhin",
  "context/phone": "+2519****47",
  "context/reporting_branch-region": "RE-014",
  "context/reporting_gps": "14.076213 38.79844 0 0",
  "context/alert-type": "Onset",
  "context/alert-source": "local_gov_trigger",
  "context/gov_endorse": "yes",
  "context/start_date": "2026-08-15",
  "context/hazard": "Wind storm",
  "context/general_description": "Due to El Niño–related weather conditions in 2026, Tigray Region has experienced recurrent and unexpected windstorms across several woredas and kebeles in different zones. Windstorm incidents continued during August 2026, particularly in the Eastern, Central, and North Western Zones, causing significant damage to communities, agricultural production, livestock, residential houses, schools, and other community assets.",
  "geo/setting": "rural",
  "geo/location_scope": "zone",
  "geo/region-one": "Tigray",
  "geo/zone-multiple": "Central Eastern North_Western",
  "ppl_impact_group/ppl_before": "282652",
  "ppl_impact_group/ppl_affected_show": "yes",
  "ppl_impact_group/ppl_affected": "41836",
  "ppl_impact_group/ppl_affected_displaced": "0",
  "ppl_impact_group/ppl_affected_non-displaced": "41836",
  "ppl_impact_group/ppl_returned": "0",
  "ppl_impact_group/ppl_current": "41836",
  "ppl_impact_group/ppl_x100_affected": "14",
  "ppl_impact_group/ppl_dead": "0",
  "ppl_impact_group/ppl_wounded": "0",
  "ppl_impact_group/ppl_missing": "0",
  "ppl_impact_group/population_impact": "The most severely affected communities were reported in the woredas listed in the table below. The incidents resulted in extensive crop damage, livestock losses, and destruction of residential houses and school facilities. Overall, the reported windstorm incidents affected approximately 7,142 households (41,836 people), with more than 1,000 hectares of cropland damaged.",
  "accessibity/facility_damage_level": "No_damage",
  "accessibity/impact_on_personnel": "no",
  "accessibity/access_condition": "fully_accessible",
  "accessibity/general_response_summary": "In 2026, El Niño–related weather conditions have caused recurrent windstorms across Tigray Region, with incidents continuing in August, particularly in the Eastern, Central, and North Western Zones. The windstorms have caused significant damage to crops, livestock, residential houses, schools, and community assets, affecting approximately 7,142 households (41,836 people) and damaging more than 1,000 hectares of cropland. These impacts have further increased the vulnerability of farming households already facing humanitarian challenges. Urgent multi-sectoral assistance is needed, including food and cash assistance, emergency shelter and household items, WaSH, health and protection services, and livelihood recovery support.",
  "emergency_code/unique_code": "EM-20260815-Wind storm-Tigray-zone",
  "__version__": "v4KBzqarLeX4vgfemsCi5K",
  "meta/instanceID": "uuid:8160155d-0177-4c39-ad72-15a851317a76",
  "_xform_id_string": "aydYC8AYCDuX7y4PwfvgrX",
  "_uuid": "8160155d-0177-4c39-ad72-15a851317a76",
  "meta/rootUuid": "uuid:8160155d-0177-4c39-ad72-15a851317a76",
  "_attachments": [],
  "_status": "submitted_via_web",
  "_geolocation": [
    14.076213,
    38.79844
  ],
  "_submission_time": "2026-08-24T12:20:18",
  "_validation_status": {},
  "_submitted_by": "tigrayeoc"
}
```

### 3.2 Emergency Alert — selected fields (2nd record)

```json
{
  "_id": 14730514,
  "emergency_code/unique_code": "EM-20260701-conflict-Amhara-woreda",
  "context/alert-type": "Onset",
  "context/hazard": "conflict",
  "context/start_date": "2026-07-01",
  "geo/region-one": "Amhara",
  "geo/location_scope": "woreda",
  "ppl_impact_group/ppl_affected": "5883",
  "accessibity/access_condition": "fully_accessible",
  "_submission_time": "2026-08-19T06:28:21",
  "_submitted_by": null
}
```

### 3.3 Rapid Needs Assessment — selected fields

```json
{
  "_id": 14789450,
  "context/emergency-selection": "EM-20260812-drought-Amhara-zone",
  "context/date_of_reported": "2026-08-17T10:16:16.233+03:00",
  "context/prepared_by": "Yaregal Denekew",
  "context/phone": "0913****16",
  "context/reporting_branch": "Amhara_Regional_Office_Branch",
  "location/region": "Amhara",
  "location/zone": "North_Gondar",
  "location/woreda": "Debark",
  "location/kebele": "62",
  "ppl_impact_group/ppl_affected": "318443",
  "ppl_impact_group/ppl_affected_displaced": "19318",
  "ppl_impact_group/ppl_in_need": "318443",
  "sector/severity/food_con": "5",
  "sector/severity/wash_con": "5",
  "assistance/food_needs": "5",
  "priority_sectors/sector1": "food",
  "priority_sectors/sector2": "wash",
  "priority_sectors/sector3": "health",
  "response_modalities/modality1": "Modality1",
  "rna_photos": "photo_2026-08-24_09-53-45-9_53_54.jpg",
  "_submission_time": "2026-08-24T06:53:58",
  "_validation_status": {
    "timestamp": 1787569903,
    "uid": "validation_status_approved",
    "by_whom": "ercseoc2019",
    "label": "Approved"
  }
}
```

### 3.4 Emergency Field — selected fields

```json
{
  "_id": 14786833,
  "context/emergency-selection": "EM-20250301-drought-Oromia-zone",
  "context/emergency_status": "no",
  "context/period-start_date": "2026-08-11",
  "context/period-end_date": "2026-08-23",
  "context/reporting_days": "12",
  "context/prepared_by": "Adugna Abdissa",
  "context/reporting_branch": "RE-008",
  "location/region-one": "Oromia",
  "location/zone-multiple": "East_Bale East_Hararge West_Arsi West_Hararge",
  "branch_sitrep/action_taken": "assessment_ercs",
  "branch_sitrep/reached_population/g_reach": "0",
  "branch_sitrep/reached_population/Disag_yes_no": "no",
  "branch_sitrep/resources_group/resources_staff": "8",
  "branch_sitrep/resources_group/resources_volunteers": "3",
  "branch_sitrep/resources_group/resources_BDRT": "7",
  "branch_sitrep/resources_group/support_required": "allocation_funds_response relief_nfi coordination",
  "actors/actors_present": "government_agencies ingos",
  "_submission_time": "2026-08-23T19:06:14",
  "_validation_status": {
    "timestamp": 1787512018,
    "uid": "validation_status_approved",
    "by_whom": "ercsoromia",
    "label": "Approved"
  }
}
```

### 3.5 Response Reporting — full record

```json
{
  "_id": 12168772,
  "formhub/uuid": "496cc2c29ebf45b482240438f231dea5",
  "start": "2026-02-12T09:50:41.982+03:00",
  "end": "2026-02-12T12:12:07.910+03:00",
  "today": "2026-02-12",
  "enumerator": "Kidu Gebremedhin",
  "report_month": "2026-04-01",
  "location/region": "Tigray",
  "location/zone": "North Western",
  "location/woreda": "Asgede",
  "crisis": "conflict",
  "sector": "Food",
  "partner": "ERCS_Hum",
  "activity": "hygiene_promotion",
  "beneficiaries/hh_reached": "656",
  "beneficiaries/people_reached": "656",
  "beneficiaries/girls_under5_hhm": "123",
  "beneficiaries/boys_under5_hhm": "118",
  "beneficiaries/female_hhm": "377",
  "beneficiaries/male_hhm": "279",
  "beneficiaries/disability": "129",
  "beneficiaries/disability_001": "69",
  "beneficiaries/disability_002": "60",
  "budget_utilised": "656",
  "Location_datacollected_area": "14.177355 37.72438 0 0",
  "__version__": "vXPhtavSgnGfZNwBBvDaEK",
  "meta/instanceID": "uuid:0f15ea94-0d3f-46b7-85f1-816d1eb4865f",
  "_xform_id_string": "a8k4JQNvj4bcrr8yt7zhTa",
  "_uuid": "0f15ea94-0d3f-46b7-85f1-816d1eb4865f",
  "meta/rootUuid": "uuid:0f15ea94-0d3f-46b7-85f1-816d1eb4865f",
  "_attachments": [],
  "_status": "submitted_via_web",
  "_geolocation": [
    14.177355,
    37.72438
  ],
  "_submission_time": "2026-02-12T09:12:06",
  "_validation_status": {},
  "_submitted_by": null
}
```

### 3.6 Response Reporting — selected fields (2nd record)

```json
{
  "_id": 11963064,
  "report_month": "2025-12-01",
  "location/region": "Tigray",
  "location/zone": "Central",
  "crisis": "drought",
  "sector": "Cash",
  "partner": "EU_ECHO",
  "activity": "distribution_cash",
  "beneficiaries/hh_reached": "1500",
  "beneficiaries/people_reached": "7269",
  "beneficiaries/disability": "7269",
  "beneficiaries/disability_001": "107",
  "beneficiaries/disability_002": "176",
  "budget_utilised": "18075000",
  "_submission_time": "2026-01-22T08:31:29"
}
```
