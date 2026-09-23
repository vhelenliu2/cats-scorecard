---
name: goal-step0-registrar
description: Step 0 of the Goal Creation & Pacing Workflow (Registrar). Resolve the metric to a stable metric_id, read what the Goal Registry already knows, detect existing or conflicting goals, classify the goal shape, and route to the correct path. Always run this before Steps 1-5.
---

# Step 0: The Registrar (Intake & Routing)

**Purpose**: Decide *which* goal-setting path this metric needs — before doing any analysis.

**Why this step exists**: The workflow used to assume every goal is derived bottom-up from
history. For this metric set that is the *minority* case. Running the Topographer on a metric
whose goal was already committed by Finance produces a competing number; running it on a derived
metric like eCPM produces a number that contradicts its own inputs. Step 0 prevents both.

**Non-negotiable outcome**: a `metric_id`, a goal shape, a named approver, and a route. Nothing
downstream may proceed without all four.

---

## Step 0.1: Resolve the metric to a `metric_id` (never a display name)

> **Read to the user**: *"First I'll pin this metric to its registry ID. Display names drift —
> we've had goals silently go blank because a sheet label changed — so everything downstream keys
> on the ID."*

1. Look up the metric in the **Metric Registry**
   ([`governance/seed/company_level/metric_registry_seed.csv`](../../../governance/seed/company_level/metric_registry_seed.csv)
   and [`governance/seed/metric_registry_seed.csv`](../../../governance/seed/metric_registry_seed.csv)).
2. If the user's wording doesn't match a `display_name`, check the **Metric Alias Map** tab before
   guessing.
3. If there is genuinely no record, **stop** and create the Metric Registry row first. A goal
   cannot exist without a metric to attach it to.

`metric_id` is `MET-` + first 12 hex chars of the SHA-256 of the display name
([`apply_governance_warnings.py`](../../../hex_edits/TO_PASTE/apply_governance_warnings.py)).
Derive it, don't invent it.

### Retired names you will encounter

The governance tracker still carries names that were renamed in code. Resolve these before
proceeding:

| Legacy name in tracker/sheets | Current name |
|---|---|
| CVR A/B | kiCR4 A/B |
| IIR A/B | PilR A/B |
| CPI A/B | Post-Install CPA A/B |

**Gate 0.1**: `metric_id` confirmed. Record it verbatim.

---

## Step 0.2: Read what the registry already knows

Most of what the baseline workflow *asked the stakeholder* is already recorded. Read it instead of
asking.

| Registry field | What it tells you | Replaces which old question |
|---|---|---|
| `goal_policy` | `Required` / `No goal by design` / `Pending decision` | "Do we even want a goal?" |
| `status_rule` | The RAG policy already wired in code | All of Step 4's policy selection |
| `cadence` | `Daily` / `Quarterly` | Pacing granularity |
| `accountable_owner_id` | Who owns the number | "Who owns this metric?" |
| `goal_source_id` | Where the goal is supposed to come from | "Where should I look?" |
| `tier` | Tier 0 / 1 / 2 | Approval rigour required |
| `health` | `Healthy` / `Due` / `Stale` / `Missing` / `Blocked` | Whether the metric is trustworthy right now |

> **Read to the user**: *"The registry already says this is a **[tier]** metric owned by
> **[owner]**, with `goal_policy = [policy]` and `status_rule = [rule]`, and the goal is supposed
> to come from **[source]**. I'll work from that unless you tell me it's wrong."*

**If `goal_policy = No goal by design`** → jump to **Route D**. Do not analyse.
**If `health = Blocked`** → resolve the block before setting a goal.

---

## Step 0.3: Detect goals that already exist — including conflicts

**This is the highest-value check in the entire workflow.** The problem being solved is not "we
have no goals," it is "we have goals in several places and they disagree."

Search **all four** locations before concluding a goal is missing:

| # | Location | How to check |
|---|---|---|
| 1 | Goal Registry | Row for this `metric_id` + `planning_period` with a non-null `target_value` |
| 2 | Hardcoded Python literals | Grep `hex_edits/modules/tabs/` and `hex_edits/TO_PASTE/` for the metric and for `_GOALS`, `_goal`, `_q_goal`, `_year_goal` |
| 3 | Google Sheets | Whatever `goal_source_id` resolves to |
| 4 | Warehouse | e.g. `daily_quota_profile`, `raw_official_target_platform` |

### If two or more sources disagree — STOP

> **Read to the user**: *"I found more than one goal for this metric and period, and they don't
> match:*
> - *[Source A]: [value] — [file:line]*
> - *[Source B]: [value] — [file:line]*
> - *Difference: [absolute] ([percent]%)*
>
> *I'm not going to set a third number on top of these. This needs [owner] to say which is
> canonical. Want me to open a Maintenance Queue task?"*

**Do not derive a new goal to break a tie.** Record both candidates with provenance, set
`status = Conflicting sources`, and escalate. A workflow that quietly invents a third value makes
fragmentation worse.

**Worked example — Ad Impressions Q3 2026** (a real conflict in this repo):

| Source | Value | Location |
|---|---|---|
| `IMPRESSIONS_GOALS['Q3 2026']` | US 59.8B + ROW 57.9B = 117.7B | `company_level_goals.py:381` |
| `legacy_impressions_goal_full_q` | 112.33B | `cats-scorecard.draft.yaml:13265` |

4.8% apart, both live, governance health `Missing`. Correct behaviour is escalation, not a fourth number.

**Gate 0.3**: Existing-goal search complete. Conflicts escalated rather than averaged.

---

## Step 0.4: Establish metric direction (before any scenario math)

> **Ask**: *"For this metric, is higher better or lower better?"*

This maps to `indicator.value` (`+1` / `−1`) — the only place the codebase encodes direction.

**It is not cosmetic.** Step 2's scenario multipliers, trend glyphs, and declining-segment
reframe are all written for higher-is-better. For a cost metric (CPC, kCPA4, CPA, CPV6) the
literal reading of "Aggressive = momentum × 1.2" sets a **worse** goal the more ambitious you ask
to be.

| Direction | Examples | Effect downstream |
|---|---|---|
| Higher is better | Revenue, Impressions, MAA, DAUq, CTR, ROAS | Step 2 as written |
| **Lower is better** | CPC, kCPA4, CPA, CPV6, cost-per-anything | **Invert** glyphs, multipliers, and bands |

**Gate 0.4**: Direction recorded.

---

## Step 0.5: Classify the goal shape and route

Ask at most these three questions, then route:

1. *"Has someone already committed this number to Finance, the board, or a plan?"*
2. *"Is this metric calculated from other metrics that have their own goals?"*
3. *"Do we have actuals flowing for it today?"*

### Routing table

| Route | Condition | What happens | Skip |
|---|---|---|---|
| **A — Register (top-down)** | A number is already committed externally | Validate feasibility against history, then register it | Step 2 derivation |
| **B — Derive (bottom-up)** | No committed number; actuals exist with history | Full Steps 1 → 2 → 3 → 4 | nothing |
| **C — Dependent (derived metric)** | Metric = f(other metrics) | Compute goal arithmetically from parents; block if any parent unset | Steps 1, 2 |
| **D — No goal by design** | `goal_policy = No goal by design` | Record the decision with owner + rationale, exit | Steps 1–4 |
| **E — Blocked** | No actuals pipeline, or goal source not wired up | Register intent, open queue task, exit | Steps 1–4 |

### Route A — Register a committed goal

The **most common** route for Tier 0/1 metrics. The job is *not* to derive a number; it is to
validate and record one.

Do this:
1. Record the committed value and where it came from (`approval_reference`).
2. Run a **feasibility check only** — required run-rate vs recent actuals:
   > *"The committed goal is [X]. That needs [Y] per day for the rest of the quarter, versus
   > [Z] per day recently — a [W]% change. Flagging this as [achievable / a stretch / not
   > credible]."*
3. If not credible, report it — do **not** silently substitute your own number.
4. Go straight to Step 3 (Pacer), then Step 5 (Publisher).

Applies to: Ads Realized Revenue, Ad Impressions, Upper Funnel Revenue, Overall Measured Revenue,
Shopping Revenue.

### Route C — Dependent metric

Never analyse a derived metric as if it were independent.

> *"eCPM is realized revenue ÷ impressions × 1000. It can't have an independent goal — it's
> whatever the revenue and impressions goals imply. Revenue goal is [A], impressions goal is [B],
> so eCPM = [A ÷ B × 1000]. If either parent changes, this changes."*

If a parent goal is unset or conflicting, **block**: `status = Blocked on parent goal`. For eCPM
today that means blocked on the Ad Impressions conflict from Step 0.3.

### Route D — No goal by design

A legitimate, valid end state — not a failure. Applies to gROAS\*, Reach/Frequency/Depth,
Retention 28D (SMB).

Record and exit:

| Field | Value |
|---|---|
| `goal_policy` | `No goal by design` |
| `target_type` | `No goal by design` |
| `target_value` | *(null)* |
| `approval_reference` | who decided and where |
| `approved_at` | date |
| `status` | `Approved` |

This is what stops a deliberate decision from resurfacing forever as an ambiguous "Missing."

### Route E — Blocked

Two sub-cases, both requiring the goal to be *recorded* even though it can't be *paced*:

| Sub-case | Example | `status` |
|---|---|---|
| No actuals pipeline | Revenue/FTE (`qtd = 'TBD'`), 4 Scale Our Foundations metrics | `Missing actuals pipeline` |
| Goal source named but not wired | Thriving Communities ("2026 Community Growth Plan"), % top-200 brand advertisers | `Pending decision` |

Register the target value if one is known — a hardcoded literal today is still a real commitment
and belongs in the registry with attribution.

**Gate 0.5**: Route selected and stated out loud.

---

## Step 0.6: Capture the approver up front

Collect this **now**, not at publish time — by Step 5 the context is gone. These four fields are
what make a goal auditable, and their absence is the core failure named in
[`METRICS_DATA_ARCHITECTURE.md`](../../../hex_edits/METRICS_DATA_ARCHITECTURE.md) §3.3:
*"no audit trail beyond this chat transcript of who asked for what value and when."*

| Field | Question |
|---|---|
| `target_owner_id` | "Who owns hitting this number?" |
| `approved_source_id` | "Which system or sheet is the goal's source of record?" |
| `approval_reference` | "Where was it agreed — doc link, meeting, planning cycle?" |
| `approved_at` | "When was it agreed?" |

If the user can't answer `approval_reference`, set `status = Owner confirmation required` and do
not mark the goal Approved. **An unattributed goal is not a goal.**

**Gate 0.6**: All four captured, or status downgraded.

---

## Output: Goal Intake Record (required)

```markdown
## Goal Intake Record

| Field | Value |
|---|---|
| metric_id | MET-XXXXXXXXXXXX |
| display_name | [name] |
| tier | [Tier 0/1/2] |
| planning_period | [Q3 2026] |
| direction | [higher-is-better / lower-is-better] |
| metric_type | [Total / Average / Snapshot / Rolling-LTM / Ratio / Progress-to-ceiling] |
| goal_policy | [Required / No goal by design / Pending decision] |
| status_rule | [from registry — see REFERENCE_status_policies.md] |
| **route** | **[A Register / B Derive / C Dependent / D No-goal / E Blocked]** |
| existing goals found | [list with values + file:line, or "none"] |
| conflicts | [none / ESCALATED: details] |
| target_owner_id | OWN-XXXXXXXXXXXX |
| approved_source_id | SRC-XXXXXXXXXXXX |
| approval_reference | [doc / meeting / cycle] |
| approved_at | [date] |
| steps to run | [e.g. "Route A → Step 3, Step 5"] |
```

Persist to `docs/goals/[metric_id]_[period]_intake.md` and append to the run state file
(see the orchestrator).

---

## Checklist

- [ ] `metric_id` resolved from the registry, not invented (Gate 0.1)
- [ ] Registry fields read; stakeholder not asked what's already recorded (0.2)
- [ ] All four goal locations searched (0.3)
- [ ] Conflicts escalated, **not** averaged or overwritten (0.3)
- [ ] Direction established before any scenario math (0.4)
- [ ] Route selected and stated (0.5)
- [ ] Owner + approval reference captured, or status downgraded (0.6)
- [ ] Goal Intake Record written

**Next step**: follow the route.
Route A → Step 3 · Route B → Step 1 · Route C → Step 3 · Routes D/E → Step 5 (record and exit).
