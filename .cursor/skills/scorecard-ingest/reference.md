# Scorecard ingest — reference

Read from [SKILL.md](SKILL.md). This file is the contract and source map.

## Staging Facts schema

One row per `metric_id + field_kind + period_type + planning_period`.

| column | required | notes |
|---|---|---|
| `metric_id` | yes* | `MET-` + 12 hex. Empty only for unregistered segments |
| `display_name` | yes | Registry name when known; Hex name for unregistered segments |
| `field_kind` | yes | `goal` or `actual` |
| `planning_period` | yes | `Q3 2026` or `FY 2026` |
| `period_type` | yes | `current_quarter` · `qtd` · `fy` |
| `as_of_date` | yes | ISO date used for the pull |
| `value` | no | Absolute, unformatted. DAUq = users. Null if unmatched |
| `unit` | yes | `count` · `users` |
| `source_id` | yes | `SRC-…` |
| `source_url` | yes | Full docs.google.com link with gid |
| `source_tab` | yes | Worksheet title actually read |
| `source_cell_hint` | no | e.g. `Latest Forecast!Q3 2026 Total` |
| `row_matched` | yes | `true`/`false` |
| `confidence` | yes | `high` · `review` · `blocked` |
| `review_reason` | no | Machine token + short detail |
| `approval_status` | yes | `extracted_unconfirmed` until DS/owner confirms |
| `freshness_flag` | yes | `current` · `unconfirmed` · `stale` · `late` |
| `publish_ready` | yes | Hex may treat as current **only** if true |
| `pulled_at` | yes | ISO timestamp |
| `last_verified_at` | no | Set when DS confirms |
| `verified_by` | no | Email / agent id |
| `hex_display_name` | no | If different from registry name |
| `parent_metric_id` | no | For segments |

\* Unregistered segments leave `metric_id` blank and must have
`publish_ready=false`.

### Tolerances (Hex vs staging)

| metric | check | tolerance |
|---|---|---|
| MAA | integer counts | exact after `int(value)` |
| DAUq | absolute users | 0.05M (`50_000` users) — sheet notes like `130.3<<< …` |
| DAUq geos | US + ROW vs Total | 0.1M |
| MAA segments | LCS+MM+SMB vs Overall | warn only; they are not required to sum |

## Source layouts (what the extractors assume)

### MAA — `Daily Goals Allocation`

Hex cells: `Maa goals gsheet` then `Maa goals df`.

- Skip a blank leading row; header row contains `Date` and `Overall`.
- Data rows: `Date`, `Overall`, optional `Global LCS` / `Global MM` / `Global SMB`.
- EOQ goal = row on `end_of_quarter`, else last date inside the quarter, else
  last row on or before EOQ (`lookup_sheet_row_on_or_before` in
  `hex_edits/modules/tabs/company_level_goals.py`).
- QTD goal = row on `latest_date`, else on or before.
- FY goal = 31 Dec of `as_of.year`, else on or before.

### DAUq — `Latest Forecast` (gid `964936431`)

Hex cells: `DAUq targets gsheet` then `DAUq official targets df`.
Parser: `hex_edits/TO_PASTE/dauq_official_targets_df.py`.

- Find the current-quarter label in the first 40 rows (`Q3 2026`, `Q3'26`, `Q3/2026`).
- Labels in column B. Sections: `US` → US, `RoW`/`ROW` → ROW, `Global` → Total.
- Take the `Total` row under each section in the quarter column.
- Stop before `Paid UA Spend` or an `App` block after Global.
- Values in millions (`130.3`); staging multiplies by `1_000_000` when `0 < v < 1000`.
- If ROW missing, derive Total − US.

## Hex runtime

Project `01975b00-b9bb-7006-9858-cb987fd035ae`. Current cell IDs are in
`catalog.json` (`hex_cells`). They changed when the notebook was restructured;
do not use IDs from old `*.hex.yaml` exports without listing cells first:

```bash
hex cell list 01975b00-b9bb-7006-9858-cb987fd035ae -n 100 --json
```

Targeted runs only:

```bash
hex cell run 01a03ad4-284f-739b-830e-1aeb35887eb3   # Maa goals df
hex cell run 01a03ad4-284f-739b-830e-173ab390d051   # DAUq official targets df
```

`hex cell get` is often Forbidden on this project; `hex cell list` / `hex cell run` work.

## Credentials

| location | use |
|---|---|
| Hex secret `GOOGLE_SHEETS_CONNECTION` | Hex cells |
| env `GOOGLE_SHEETS_CONNECTION` | local `run_pilot.py --mode gsheet` (JSON string) |
| env `GOOGLE_APPLICATION_CREDENTIALS` | path to service-account JSON |
| env `CATS_STAGING_SHEET_ID` | reuse an existing staging workbook |

The service account must be able to **read** both source sheets and **write**
the staging workbook. First `--push` creates the workbook and prints the URL;
share it with DS and keep the ID in `CATS_STAGING_SHEET_ID` /
`docs/ingestion/_state/pilot.md`.

## Backlog (not in this skill yet)

Google Sheet / tracker **actuals** and remaining DS target sheets from the
source-review plan: Scale OE / Cloud / ML, C performance A/B goals, Shopping
3H tracker, tickets, Thriving Communities, % top-200 brand advertisers.
Add a catalog row + extractor; do not fork the staging schema.

## Related contracts

- [METRICS_DATA_ARCHITECTURE.md](../../../hex_edits/METRICS_DATA_ARCHITECTURE.md) §5.2 Layer 1
- [DASHBOARD_WARNING_CONTRACT.md](../../../governance/DASHBOARD_WARNING_CONTRACT.md)
- [goal-step5-publisher](../goal-step5-publisher/SKILL.md) — staging is not the Goal Registry; confirmed goals still publish there separately
