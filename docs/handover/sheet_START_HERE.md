# START HERE — unused

This was a paste for leftover **Metric Registry / Goal Registry / Alias Map** tabs. Those tabs are unused. Do not add this to the live tracker. The live tracker is the [governance sheet](https://docs.google.com/spreadsheets/d/1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc).

---

# Original paste (do not use)

Create a tab named `START HERE`. Put it first. Paste the table below into A1. Do not change Metric Registry rows as part of this paste.

| | |
|---|---|
| This workbook | CATS Scorecard metric system of record. Hex displays; this sheet governs. |
| Published app | https://app.hex.tech/reddit/app/CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks/latest |
| Draft notebook | https://app.hex.tech/reddit/hex/CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks/draft/logic |
| Handover docs (repo) | [docs/handover/README.md](README.md) |
| Join key | `metric_id` (MET-…). Never join Hex to this sheet on display name. |
| | |
| How to find a metric | Metric Registry → filter display_name → copy metric_id → check Alias Map if the Hex label differs. |
| How to change a goal | Goal Registry + the live source Hex actually reads (often a planning sheet or a Python literal). Log it on Change Log. |
| How to rename | Add Alias Map row. Keep metric_id. Update Hex MetricBuilder name + Glossary together. |
| How to retire | active=FALSE, health=Retired. Do not delete. |
| Weekly | CATS Governance menu → Run governance checks. Review Health + Maintenance Queue. |
| Email alerts | OFF until Owner Map emails are clean. Leave them off. |
| | |
| Do not touch | Tabs `CATS-SC KPIS`, `Company-level goals summary`, `Company-level goals target and`. |
| Do not invent | A new metric_id by hashing a Hex label. DAUq Hex name is `DAUq (QTD), #`; registry is `DAUq (QTD), M` → always `MET-419D6C123B19`. |
| Do not show | 0 when a value is missing. Dashboard must say Not available. |
| No goal by design | Tracking metric. That is Healthy if actuals are fresh — not Missing. |
| | |
| Known aliases | CVR A/B → kiCR4 / kICR4 A/B. IIR A/B → PilR / PiIR A/B. CPI A/B → Post-Install CPA A/B. M10n Operational Excellence → Operational Excellence (as of {month}). |
| DAUq actuals | Warehouse cube, not inter_pacing_*. Parent report: Daily DAUq Report v2. |
| Small Hex fix | Run the Metrics cell + its Table cell. Do not rerun the whole notebook. |

## Alias rows to add (if missing on Metric Alias Map)

Paste onto `Metric Alias Map` (do not overwrite existing approved aliases).

| alias_name | metric_id | source_system | active | notes |
|---|---|---|---|---|
| DAUq (QTD), # | MET-419D6C123B19 | Hex | TRUE | Registry display is DAUq (QTD), M |
| DAUq (QTD), M | MET-419D6C123B19 | Metric Registry | TRUE | Canonical registry name |
| kiCR4 A/B | MET-CA604E975DD7 | Hex KPI tab | TRUE | Retired Hex/sheet label CVR A/B |
| kICR4 A/B | MET-04E4CF590909 | Hex Company Level | TRUE | Registry also has klCR4 A/B |
| klCR4 A/B | MET-04E4CF590909 | Metric Registry | TRUE | Typo-stable id; Hex prints kICR4 |
| PilR A/B | MET-350D699EBE0F | Hex | TRUE | Also PiIR A/B |
| PiIR A/B | MET-350D699EBE0F | Hex / A/B sheet | TRUE | Company Level goals key |
| IIR A/B | MET-DFE94387DAC5 | Legacy tracker | TRUE | Retired label |
| Post-Install CPA A/B | MET-929F6596484D | Hex KPI tab | TRUE | Goals key `Post-Install CPA A/B`; actuals from tracker column `Post-Install Cost (CPA)` |
| Price: Post-Install CPA | MET-929F6596484D | A/B goals sheet | TRUE | Must map to `Post-Install CPA A/B` in Hex **Canonical Metric Map** |
| CPA A/B | *(plain CPA if published)* | A/B goals sheet | TRUE | Separate from Post-Install CPA; not displayed on Company Level today |
| CPI A/B | MET-3B8912A23362 | Legacy tracker | TRUE | Retired label |
| Operational Excellence (as of {month}), sum | MET-A72CEBA8C5CB | Hex | TRUE | Retired name M10n Operational Excellence |
