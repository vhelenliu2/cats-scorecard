# Deliverable 5 — Recommendation

## The headline

**Productionize the registry contract. Automate detection and validation. Keep goal-setting
judgement manual.**

The instinct behind this project — "make goaling standardized so stakeholders don't have to do
much" — is right, but the leverage is not where the baseline skills put it. They spend 49% of their
instructions on *analysis* and 3% on *storage*. The evidence says invert that.

On the one metric taken end-to-end against live data, the analysis was the easy part: a single
aggregating SQL statement produced everything needed in ~3 minutes. What went wrong was at the ends
— the workflow couldn't tell that **two conflicting goals already existed**, and had **nowhere to
put** the result. That is why goals are still Python literals, and no amount of better scenario
modelling fixes it.

The batch picture makes this concrete. Of 15 required company-level goals:

| Category | Count | Work required |
|---|---:|---|
| Already have a committed goal (Route A) | ~3 | Register + validate |
| Conflicting goals | 1 | **Escalate** — Ad Impressions |
| Blocked on a parent | 1 | eCPM, waiting on impressions |
| `No goal by design` | 3 | File the decision |
| No actuals pipeline | ~5 | Register intent, queue the pipeline |
| **Genuinely need derivation** | **~2** | Full analytical workflow |

**~13 of 15 need bookkeeping and coordination, not analysis.** Automating analysis optimises the
2. Automating the record optimises the 13.

---

## What to productionize

### P1 — The Goal Registry as the single system of record

Already ~90% built. `governance/build_seed.py` defines the schema, the Apps Script control plane
exists, and `MAINTENANCE_RUNBOOK.md` defines the quarterly lock. What's missing is that **nothing
writes goal values into it** — all 15 rows are empty stubs.

Do this:
1. **Backfill every hardcoded goal** with attribution (`approval_reference = "backfilled from
   file:line"`, `status = Owner confirmation required`). Roughly 20 values across Upper Funnel,
   Shopping, Measured Revenue, HQ Signal, Revenue/FTE, 4 Scale metrics, `IMPRESSIONS_GOALS`, MAA
   `previous_quarter_exit`, DAUq overrides.
2. **Make the dashboard read goals from the registry** rather than literals — the Layer 2 idea from
   the architecture doc §5.3, migrating one theme at a time.
3. **Record the `No goal by design` decisions** (3 metrics) so they stop appearing as ambiguous
   "Missing".

Highest value per unit of effort in the entire project: it converts "who typed $310M and when" from
unanswerable to a lookup.

### P2 — The validator in CI

[`validate_goal_row.py`](../../governance/validate_goal_row.py) already catches formatted values,
percent-vs-decimal errors, missing approval trails, supersede violations, and — critically —
`status_rule` values that don't exist. Run it on every registry change.

It caught `pacing_standard`, a policy the **old Step 4 skill actively recommended** and which would
raise `ValueError` and crash the dashboard. That class of error should never depend on someone
remembering a rule.

### P3 — Fix the five status-layer defects

Documented in [`REFERENCE_status_policies.md`](REFERENCE_status_policies.md). Two are urgent:

- **D1** — `dauq` compares an absolute goal against `>= 1`, so any real DAUq goal renders
  **permanently Green**. A Tier 0 metric silently always-green is worse than no goal. **Fix before
  wiring any DAUq goal.**
- **D2** — `goal`, the registry's most common rule, has no None guard: `None >= 1.0` raises
  `TypeError`. MAA, DAUq and Thriving Communities all use it and all currently have unset goals.

D3 (no ceiling goals), D4 (relative bands unsafe near a ceiling) and D5 (narrowing bands don't
exist) need product decisions first.

---

## What to automate

Automate **detection**, not decisions. Each of these is deterministic, runs unattended, and
currently costs someone hours of manual reading.

| # | Automation | Replaces | Detects |
|---|---|---|---|
| **A1** | **Goal conflict scan** — for each `metric_id` × period, compare registry, Python literals, sheets, warehouse | Nothing (this is why the impressions conflict survived) | Duplicate/disagreeing goals |
| **A2** | **Missing-goal report** — Metric Registry rows with `goal_policy = Required` and no approved goal | Manual re-reading of a tracker sheet | Quarterly lock gaps, per owner |
| **A3** | **`status_rule` validation** — every rule resolves against the 23 real strategies | Nothing | Dashboard-crashing config |
| **A4** | **Coherence checks** — segments sum to total; quarters sum to FY (skipping Rolling-LTM) | Nothing | Shopping's unverifiable ladder; Measured Revenue ✅ |
| **A5** | **Staleness/plausibility scan** — goal implies a QoQ decline on a growing metric, or is below last quarter's actual | Nothing | Exactly the stale 112.33B impressions goal |
| **A6** | **Label-drift check** — every sheet label maps to a known `metric_id`, fail loudly on unmapped | Multi-hour debugging | The Post-Install CPA bug class |

**A1 and A5 together would have caught the impressions problem without a human looking.** A5 is
notably cheap: "is the goal below last quarter's actual on a metric that keeps growing?" is a
one-line check that flags a class of silent staleness nobody currently looks for.

These extend the existing daily governance scan rather than needing new infrastructure.

### Automate with a human gate

| Task | Why gated |
|---|---|
| Backfilling hardcoded goals | Mechanical, but every row needs owner confirmation before `Approved` |
| Pacing curve generation | Deterministic once the shape is chosen — but the shape choice is a decision (3.90pp swing) |
| Route A feasibility checks | Computation is automatable; the "is this credible?" verdict is not |

---

## What to leave manual

**Goal-setting judgement.** Not because it can't be automated, but because automating it produces
confident wrong answers — and the whole problem here is trust in the number.

| Decision | Why manual |
|---|---|
| **Ambition level** | Genuinely a business choice. No amount of history says whether Q3 should be safe or stretch. |
| **Resolving conflicts** | The live case shows why: the evidence *narrows* it to 117.70B, but only Finance can declare canonical. An agent picking one silently is the failure mode we're fixing. |
| **Strategic context** | Launches, headwinds, and incentives exist only in people's heads. |
| **Which committed number to accept** | Route A validates and reports; it must not substitute. |
| **Whether a metric should have a goal** | `No goal by design` is a judgement, correctly an enum owned by humans. |
| **Deceleration interpretation** | Live: YoY fell +52.5% → +17.3%. Whether that's maturation or a fixable problem determines the goal, and no model knows which. |

**The sharpest illustration**: on Ad Impressions, the committed goal (+12.52% YoY) is *below*
run-rate projection (+16.21%). An automated system would flag it as sandbagged. But YoY has
decelerated ~8pp/quarter for five quarters, so the conservative number is arguably the *correct*
one. Automation would have confidently recommended raising a goal that is probably right.

---

## Sequenced plan

**Now (days)** — no dependencies, immediate value
1. Ship the revised skills (done — [Deliverable 4](04_IMPROVEMENTS.md)).
2. Run the **conflict scan (A1)** and **missing-goal report (A2)** across all 15 required metrics.
3. Escalate the impressions conflict to Finance with the QoQ evidence.
4. Record the 3 `No goal by design` decisions.

**Next sprint** — the record
5. Backfill ~20 hardcoded goals with attribution.
6. Wire the **validator into CI (P2)**.
7. Fix **D1 and D2** before any new goal wiring.
8. Decide the **linear vs seasonal pacing** standard (decision #3).

**This quarter** — close the loop
9. Point the dashboard at the registry for one theme (start with revenue — simplest, highest audit value).
10. Add automations **A3–A6** to the daily governance scan.
11. Run one full quarterly lock in batch mode and measure elapsed time and stakeholder touches.

**Next quarter** — the gaps
12. Resolve the no-actuals-pipeline metrics (decision #7): build or permanently mark them.
13. Add `upper_bounded_goal` and absolute-error-budget strategies (D3, D4) if ceiling metrics matter.

---

## How to know it worked

| Measure | Today | Target |
|---|---|---|
| Goals with an approved registry row | **0 of 15** | 15 of 15 |
| Goals answering "who approved this, when" | 0 | all |
| Goals living only in Python literals | ~20 | 0 |
| Undetected goal conflicts | ≥1 (found by hand) | 0 — caught by A1 |
| Stakeholder decisions per goal | ~17 gates | ≤6 questions |
| Metrics needing real analysis per quarter | unknown | ~2 of 15, known upfront |
| Time to answer "which goals are missing?" | manual sheet read | a query |

The first three are the ones that matter. They're all about the **record**, not the analysis — which
is the whole recommendation in miniature.

---

## The one-paragraph version

Goaling here is fragmented not because teams analyse badly but because there is no canonical place
to put a goal and no check that one already exists. The governance layer that solves this is already
built and empty. So: fill it, guard it with a validator and a handful of deterministic scans, and
leave the judgement calls — ambition, conflict resolution, strategic context — with the humans who
own the numbers. Stakeholders end up doing *less* not because an agent decides for them, but because
the workflow stops asking them things the registry already knows and stops making them chase goals
that were already committed somewhere else.
