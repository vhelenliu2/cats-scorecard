---
name: goal-workflow-orchestrator
description: Orchestrates the Goal Creation & Pacing Workflow (Registrar → Topographer → Architect → Pacer → Signaler → Publisher). Routes by goal shape, persists run state to disk, and coordinates batch quarterly goal locks across many metrics and owners.
---

# Goal Creation & Pacing: Workflow Orchestrator

**Your role**: route the work, keep state on disk, and make sure every goal ends up in the Goal
Registry with an owner attached.

**The one rule that matters most**: **always run Step 0 first.** It determines which of the later
steps apply. Skipping it is how you end up inventing a third goal for a metric that already has two.

---

## The 6 steps

| Step | Name | Purpose | Skill |
|---|---|---|---|
| **0** | **Registrar** | Resolve `metric_id`, read the registry, find existing/conflicting goals, pick the route | [`goal-step0-registrar`](../goal-step0-registrar/SKILL.md) |
| 1 | Topographer | Analyse behaviour, data health, shape | [`goal-step1-topographer`](../goal-step1-topographer/SKILL.md) |
| 2 | Architect | Set or validate the goal value | [`goal-step2-architect`](../goal-step2-architect/SKILL.md) |
| 3 | Pacer | Build the QTD expectation curve | [`goal-step3-pacer`](../goal-step3-pacer/SKILL.md) |
| 4 | Signaler | Confirm the `status_rule` | [`goal-step4-signaler`](../goal-step4-signaler/SKILL.md) |
| 5 | Publisher | Write to the Goal Registry + change log | [`goal-step5-publisher`](../goal-step5-publisher/SKILL.md) |

Supporting reference: [`REFERENCE_status_policies.md`](../../../docs/goaling/REFERENCE_status_policies.md)
— the 23 valid `status_rule` values. Anything else crashes the dashboard.

---

## Routing: not every metric runs every step

Step 0 assigns a route. **Follow it** — running all five steps on every metric is the main source of
wasted effort and wrong answers.

| Route | Condition | Steps to run |
|---|---|---|
| **A — Register** | Number already committed (Finance/board/plan) | 0 → **1 (abbreviated)** → **2 (validate only)** → 3 → 4 → 5 |
| **B — Derive** | No committed number; actuals with history exist | 0 → 1 → 2 → 3 → 4 → 5 |
| **C — Dependent** | Metric = f(other metrics) | 0 → **3** → 4 → 5 *(skip 1 and 2)* |
| **D — No goal by design** | `goal_policy = No goal by design` | 0 → **5** |
| **E — Blocked** | No actuals pipeline, or goal source not wired | 0 → **5** |

**Route A is the most common route for Tier 0/1 metrics** — and it is *not* the bottom-up flow the
workflow was originally written for. Route A validates a committed number; it does not derive one.

---

## State persistence (real, not notional)

Keep run state in a file. A quarterly lock spans days and sessions; in-context tracking is lost the
moment the conversation ends.

**File**: `docs/goals/_state/[planning_period].md`

```markdown
# Goal Lock State — Q3 2026
_Updated: 2026-07-30T15:40Z_

| metric_id | display_name | route | owner | step | status | goal_id | blocker |
|---|---|---|---|---|---|---|---|
| MET-83DD772E1658 | Ad Impressions (QTD), B | A | OWN-06C3F25CA959 | 5 | Conflicting sources | — | 117.70B vs 112.33B — needs Finance |
| MET-8D540B48605D | eCPM (QTD), $ | C | OWN-06C3F25CA959 | blocked | Blocked on parent goal | — | waiting on impressions |
| MET-B61F39994E32 | MAA (R28D), # | B | OWN-C7F2E02C77AF | 2 | In progress | — | — |
```

Update it **after every step**, not at the end. On resuming, read it first and report where things
stand before doing anything new.

---

## Batch mode: the quarterly goal lock

The real job is not one metric — it is ~15 metrics across ~9 owners against a lock date. All 15
company-level Goal Registry rows are currently empty stubs. Coordination *is* the work.

### Sequence

1. **Inventory.** List every Metric Registry row where `goal_policy = Required` and `active = TRUE`.
2. **Run Step 0 on all of them first.** Cheap, and it reveals the real shape of the problem before
   any analysis: which already have goals, which conflict, which are blocked, which need deriving.
3. **Report the batch picture** before deep work (see below).
4. **Group by route.** D and E metrics finish immediately via Step 5 — clear them first for quick
   wins and a shorter list.
5. **Group remaining work by owner**, so each person is asked once rather than repeatedly.
6. **Then** run Steps 1–4 for Routes A/B/C.

### Batch status report

> *"Q3 2026 goal lock — 15 metrics required:*
> - *✅ **3** already have approved goals (Route A, register only)*
> - *⚠️ **1** has conflicting goals — Ad Impressions, 117.70B vs 112.33B, needs Finance*
> - *🔗 **1** blocked on a parent — eCPM, waiting on impressions*
> - *🚫 **3** are `No goal by design` — recordable today, no analysis needed*
> - *⛔ **5** have no actuals pipeline — goal-only, register and queue*
> - *🔍 **2** need real derivation work — MAA, Thriving Communities*
>
> *So the actual analytical work is **2 metrics**. The other 13 are registration, escalation, or
> blocked. Want me to clear the 8 quick ones first?"*

That reframing is the point of batch mode: it turns "15 goals to set" into "2 goals to set and 13
records to file."

---

## Minimising stakeholder burden

The goal is that **stakeholders don't have to do much.** The baseline workflow had ~17 decision
gates. Most were avoidable.

### Never ask what the registry already knows

| Don't ask | Read from |
|---|---|
| "Who owns this metric?" | `accountable_owner_id` |
| "How should we grade it?" | `status_rule` |
| "Do we need a goal?" | `goal_policy` |
| "Where does the goal come from?" | `goal_source_id` |
| "Daily or quarterly?" | `cadence` |

### The questions genuinely worth a stakeholder's time

1. *Is this number already committed somewhere?* (route)
2. *Higher better or lower better?* (direction — only if unclear)
3. *What ambition level?* (Route B only)
4. *Any strategic context — launches, headwinds?*
5. *Who approved this, and where is it written down?* (non-negotiable)
6. *Escalations only*: conflicts, infeasible goals, pacing-shape choices that change the colour.

**Never ask a stakeholder to choose a sMAPE tradeoff or a band width.** Those are analyst decisions
with defaults; surface them only when they change an outcome.

---

## Definition of done

A goal is done when **all** of these hold. Not before.

- [ ] Goal Registry row exists, keyed on `metric_id`, all 15 columns populated
- [ ] `status` is accurate — `Approved` **only** with a non-empty `approval_reference`
- [ ] Change Log entry appended
- [ ] `status_rule` is one of the 23 real values
- [ ] Pacing curve cross-checked against the production dashboard status
- [ ] Stakeholder deliverable written, grading rule stated in plain language
- [ ] State file updated
- [ ] Blockers and conflicts have Maintenance Queue tasks with named owners

"I produced an analysis" is **not** done. "It's in the registry with an owner" is done.

---

## Output formatting rules

### Artifacts must be clickable

Every path is a markdown link, never bare text or backticks.

✅ `Chart saved to [impressions_pacing.png](figures/impressions_pacing.png)`
❌ `Chart saved to figures/impressions_pacing.png`

Embed charts inline with `![alt](figures/…png)` so the user sees them without clicking.

### Pair every CSV with a readable twin

CSVs render as raw text in an IDE. For anything a human will review, write both
`data/[name].csv` (machine) and `data/[name].md` (human).

| Artifact | `.md` twin? |
|---|---|
| Pacing tables (<500 rows) | ✅ |
| Summary / segmentation tables | ✅ |
| Cardinality scans | ✅ |
| Raw query results (1000+ rows) | ❌ CSV only |

### Naming

Key artifacts on `metric_id`, not display name — display names drift:
`data/MET-83DD772E1658_Q3-2026_pacing.csv`

---

## How to start

**"Help me set a goal for [metric]"** → read Step 0, run it, follow the route.

**"Run the quarterly goal lock"** → batch mode: Step 0 across all required metrics, then report the
batch picture before deep work.

**Jump requests** — always confirm the prerequisite exists rather than assuming:

| Request | Action |
|---|---|
| "Just analyse this metric" | Step 0 → Step 1. Say that no goal will be registered. |
| "I have a goal, just pace it" | Step 0 (confirm no conflict), then Step 3. |
| "Re-do the traffic signaling" | Step 4. Verify against the 23 real rules. |
| "Just save it" | Step 5 — but Step 0 first, so you don't overwrite a conflicting goal. |
| "Set goals for everything" | Batch mode. |
