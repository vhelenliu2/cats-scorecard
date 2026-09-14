# Reference — Active Status Policies (authoritative)

> **Source of truth:** the Hex draft notebook **Status Strategies** cell (Shared Logic section).
> At the top of that cell, **`ACTIVE_STATUS_RULES`** lists every rule id and which live rows use it.
> The implementations live in the strategy classes in the same cell (`StatusStrategyFactory._strategies`).
>
> These are the **only 10 values** a live scorecard row may use. Anything else makes
> `StatusStrategyFactory.get_strategy()` raise `ValueError` and the tab fails to build.

## How to assign a rule

In a tab's **Metrics** cell (e.g. **CATS SC KPIs Metrics**, **Company Level Goals Metrics**):

```python
.with_status('goal_binary', 'Green: >=100% of QTD goal, Red: <100%', display=True)
```

Rows with **no** official colour target use `'grey'` (or `display=False`).

## Active rules (live scorecard)

| `status_goal` | Green | Yellow | Red | Used by |
|---|---|---|---|---|
| `goal_binary` | ≥100% of pacing bar | — | <100% | MAA (+ LCS / MM / SMB), Ads Realized Revenue, Rev/FTE, all Scale rows |
| `goal_rev_2m` | ≥99.5% of QTD goal | another **$2M** would hit goal | else | Upper Funnel Revenue (KPI tab) |
| `goal_rev_5m` | ≥99.5% of QTD goal | another **$5M** would hit goal | else | Overall Measured Revenue (KPI tab) |
| `impressions_pacing` | ≥98% | 96–98% | <96% | Input Supply — Ad Impressions *(DAUq rows are configured with this rule but forced to `grey`)* |
| `shopping_pace` | ≥85% of weekly paced target | 70–<85% | <70% | Shopping Revenue (KPI + GTM tabs) |
| `ab_goal` | CQ goal hit anytime, **or** last 15 days ≥95% | last 15 days 70–95% | last 15 days <70%; **months 1–2 = grey** | Every A/B lift row (Company Level + KPI) |
| `yoy` | YoY moving the right way (±0.5% buffer) | — | else | Supply / GTM / Input trend rows |
| `booking_quota` | Wk 1–4: ≥55% · Wk 5–8: ≥80% · Wk 9+: ≥95% | 50% / 75% / 90% | else | Input Demand — % Booking to Quota |
| `lower_bounded_goal` | `qtd ≥ goal_lower_bound` | — | below bound | GTM — Marketplace Efficiency (DPA ROAS*) |
| `grey` | always grey | — | — | eCPM, Thriving, WAUq, RFD, Retention, HQ Signal, CAPI, credit lines, AT+DPA, gROAS*, Budget, rows under review |

**Pacing** for revenue rules = `metric.qtd / metric.qtd_goal` via `get_pacing()`.

**Scale** rows use `goal_binary` but each supplies its own custom `get_pacing()` (OE compares QoQ to a rate bar, Cloud uses YTD linear path, etc.) — see the Scale section in the [operations runbook](../handover/OPERATIONS_RUNBOOK.md).

## How to change thresholds

1. Open the [Hex draft](https://app.hex.tech/reddit/hex/CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks/draft/logic?rhid=01975b00-b9bb-7006-9858-cb987fd035ae).
2. Edit the **Status Strategies** cell — adjust the strategy class for that rule (e.g. `GoalBinaryStatusStrategy`).
3. Update the matching row in **`ACTIVE_STATUS_RULES`** at the top of the same cell if row assignments changed.
4. Update this reference table so the runbook and registry stay aligned.
5. Run **Status Strategies** → the affected tab's **Metrics** cell → that tab's **Table** cell.

## How to add a new rule

Only when a metric owner signs off on a new colour framework:

1. Add a strategy class in **Status Strategies** and register it in `StatusStrategyFactory._strategies`.
2. Add one line to **`ACTIVE_STATUS_RULES`** naming which rows will use it.
3. Assign with `.with_status('<new_id>', '…', display=True)` on those rows only.
4. Update this file and the status table in the [operations runbook](../handover/OPERATIONS_RUNBOOK.md).

Do not register rules “for later” — unused ids confuse successors.

## Retired rules (removed — do not reference)

These existed in older notebook versions but **no live row uses them** anymore:

`goal`, `goal_rev`, `qoq`, `both`, `both_1`, `both_point_1`, `qtd_vs_current_q_goal`,
`value`, `qtd_pacing`, `qtd_goal`, `qtd_goal_product_adoption`, `dauq`, `bounded_goal`

If the Goal Registry still lists one of these ids, change it to an active rule or `grey` before wiring a real goal.
