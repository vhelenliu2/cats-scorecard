# Deliverable 3 — Evaluation

## Method

- **Live end-to-end run** of all five steps on **Ad Impressions (QTD), B / Q3 2026** (test case
  B1) against production BigQuery. Full numbers:
  [`eval/live_run_results_impressions_q3_2026.md`](../../eval/live_run_results_impressions_q3_2026.md).
- **Desk trace** of the remaining 16 test cases from
  [Deliverable 2](02_TEST_SET.md), following each skill's instructions literally and recording
  where they break.
- Every "needs context" and "Yoni decides" item is tied to a specific case.

Three verdict columns throughout:

| Verdict | Meaning |
|---|---|
| ✅ **Right** | The skill produced a correct, useful result unaided |
| 🟡 **Needs context** | Correct only because a human supplied information the skill never asks for |
| 🔴 **Yoni decides** | A genuine business decision the skill cannot and should not resolve alone |

---

## Part 1 — Live run, step by step

### Step 0 (did not exist) — and its absence was the first failure

Before any analysis I had to determine that Ad Impressions **already has two conflicting goals**
(117.70B vs 112.33B, 4.78% apart, both live in code). The baseline workflow has no step that looks.
Had I followed the orchestrator's instruction — *"If the user says 'Help me set a goal', start with
Step 1"* — I would have run a full topography and produced a **third** number, worsening the exact
fragmentation this project exists to fix.

🔴 **This is the single most important finding of the evaluation.** The gap is structural, not a
wording problem.

### Step 1 — Topographer ✅ mostly right, with two real wins and one wasted mandate

**What it got right:**

✅ **Fast Path triggered correctly.** Table + metric + segmentation were all known, so discovery
was correctly skipped. This saved the bulk of the work and the detection rule fired cleanly.

✅ **The partial-quarter rule earned its keep.** The raw quarterly query returns Q3 2026 at
**−64.75% YoY** — comparing 29 days against 92. Step 1 §1.4's anti-pattern rule is exactly what
prevents that number reaching a stakeholder. The like-for-like table instead gives **+16.21%**.
A 81-point swing from one methodology rule. Keep this section verbatim.

✅ **Data health check passed cleanly and cheaply.** 0 missing dates, 0 zeros, 0 spikes >3× median
across 941 days. Gate 2 correctly required no stakeholder input.

**Where it needs context:**

🟡 **Quarter length is assumed, not derived.** Q3 has 92 days; Q1 2026 had 90. Step 1 never
establishes `days_in_quarter`, but every pacing calculation downstream depends on it. I had to
supply it.

🟡 **Seasonality thresholds don't match reality.** Measured day-of-week swing is **8.97%**, which
Step 1 grades "Moderate (5–15%)". Its worked example asserts *"Strong weekly pattern — Mondays are
20% lower than Fridays."* Real spread here is Monday-high/Saturday-low at 8.97%. The example
anchors the agent toward over-reading weekly seasonality; the *within-quarter* shape (30.33% vs
31.52% linear) turned out to matter far more and Step 1 never measures it.

**Where it was wrong:**

🔴 **The mandatory sMAPE backtest was ceremony.** Step 1's checklist marks it **MANDATORY**. The
segmentation question here — split US/ROW or not? — was answered decisively in one line by the
like-for-like YoY split: **US +8.97% vs ROW +24.69%, a 15.7pp divergence.** A backtest would have
cost a second multi-minute scan to confirm what the growth split already showed. Worse, on the
nonprod connection this metric uses, a 3.5-year daily pull **did not complete in 17 minutes**
(cancelled twice) — so the mandatory step is not merely wasteful here, it is often infeasible.

### Step 2 — Architect 🟡 right framework, wrong default for this metric

**What it got right:**

✅ The **momentum snapshot** and trend glyphs describe this metric well: 🟢 growing, but 📉
decelerating.

✅ The **scenario table format** is genuinely the right artifact to put in front of a stakeholder.

**Where it fails:**

🔴 **Route mismatch.** Impressions is a *top-down committed* goal (Finance: Yona owns the number).
Step 2 is written to *derive* one. Applying its own math to live data:

| Scenario | Step 2 formula | Result |
|---|---|---:|
| Conservative | recent YoY × 0.7 | ~115.6B |
| Moderate | recent YoY × 1.0 | ~121.6B |
| Aggressive | recent YoY × 1.2 | ~125.6B |

**None of these is the committed 117.70B.** Followed literally, Step 2 tells the stakeholder their
own committed goal is between "Conservative" and "Moderate" — framing a Finance commitment as an
analyst's scenario. The correct behaviour is to *validate* 117.70B, which the skill has no path for.

🟡 **The ×0.7 / ×1.0 / ×1.2 multipliers are unjustified and interact badly with deceleration.**
Applied to a YoY *rate* on a metric whose YoY has fallen from +52.5% to +17.3% over five quarters,
"Moderate = maintain momentum" bakes in a trend that is visibly ending. The genuinely defensible
number here is the *decelerating* one — the committed 117.70B (+12.52% YoY) — which Step 2's own
framework labels sub-Conservative. The framework is anti-correlated with the right answer on this
metric.

✅ **Its sanity check would have caught the stale goal.** Step 2.4's "Reversal?" check is exactly
what flags the legacy 112.33B goal implying **−1.43% QoQ** on a metric that has grown 9 of 10
quarters. The check exists; nothing routes the conflicting candidates into it.

### Step 3 — Pacer 🔴 thin, and its default shape is measurably wrong

This step decided the outcome, and it is the second-shortest skill (146 lines).

Applying `status_rule = impressions_pacing` (Green ≥98%, Yellow 96–98%, Red <96%) to the 117.70B goal:

| Pacing shape | QTD goal | Pacing | Band | Headroom above Yellow |
|---|---:|---:|---|---:|
| **Linear** (production formula) | 37.10B | **99.38%** | 🟢 | **1.38pp** |
| **Seasonal** (Q3'25 actual shape) | 35.70B | **103.28%** | 🟢 | 5.28pp |

🔴 **The 3.90pp gap between shapes exceeds the entire 2pp Yellow band.** Q3 is mildly back-loaded
(30.33% of the quarter lands in the first 29 days, vs 31.52% linear), so linear pacing
systematically understates early performance. This metric is genuinely ahead of plan and linear
pacing puts it **1.38pp from Yellow**. In a slightly softer quarter, stakeholders get a false
"at risk" signal in month one — the fastest way to lose trust in a scorecard.

🔴 **Step 3 never mentions `previous_quarter_exit`**, which is how production actually prorates
(`status_and_metric.py:534-544`). A curve built from Step 3 will not match the dashboard.

🟡 **"Step 3.1 Shape Strategy" is three lines with no algorithm.** It says *"explicitly state the
source (e.g. 'Using Q2'25 seasonality')"* but never says how to build the shape, normalise it, or
handle differing quarter lengths. I had to construct the seasonal share myself.

### Step 4 — Signaler 🔴 unusable as written

🔴 **Every policy ID it offers is fictional.** For a cumulative volume metric it recommends
`pacing_standard` or `impressions` (narrowing 95→99%). The real registry value for this metric is
**`impressions_pacing`** (static 98/96). A stakeholder completing Step 4 selects a policy that
makes `StatusStrategyFactory.get_strategy()` raise `ValueError` — a dashboard crash, not a
degradation. Full mapping: [`REFERENCE_status_policies.md`](REFERENCE_status_policies.md).

🔴 **Narrowing bands cannot be implemented.** All 23 real strategies use static thresholds. Step 4's
most detailed section teaches a mechanic the platform does not support.

🟡 **The step is redundant here anyway.** `status_rule` is *already recorded per metric* in the
Metric Registry. For Ad Impressions it is `impressions_pacing`. Step 4 asks the stakeholder to
choose something the system already knows — burden with negative value.

✅ The **volatility-adjustment** table and the √time rationale are sound thinking, and worth keeping
as guidance for *choosing among real policies*.

### Step 5 — Publisher 🔴 dead end

🔴 Writes to BigQuery `goals_log` and `goal_pacing_daily` and cites `sql/schema_goals.sql`. **None
exists.** The live run had nowhere to land. This is why the goal is still a Python literal.

🔴 No `metric_id`, no `target_owner_id`, no `approval_reference`, no `approved_at`. After a complete
live analysis I still could not answer *"who approved 117.70B and when"* — the precise failure
[`METRICS_DATA_ARCHITECTURE.md`](../../hex_edits/METRICS_DATA_ARCHITECTURE.md) §3.3 names.

🔴 No way to record the conflict, and no `effective_to` to retire the stale 112.33B value.

---

## Part 2 — Desk trace of remaining cases

| Case | Result | Detail |
|---|---|---|
| A1 Ads Realized Revenue | 🔴 | Goal is warehouse-native in `daily_quota_profile`. Workflow re-derives instead of registering. No Route A. |
| A2 MAA | ✅ | Best-supported case. Step 2's own worked examples are MAA segments. Only gap: `previous_quarter_exit = 18_300` ramp is invisible to Step 3. |
| A3 Measured Revenue | 🟡 | Quarterly ladder sums to $1.5B correctly, but no step performs the check. Tracker/code drift (tracker "Missing", code has values) undetected. |
| B2 eCPM | 🔴 | Step 1 would cardinality-scan and sMAPE a metric with **no independent series**. Correct answer is arithmetic from parents — and it should **block**, since its impressions parent is the unresolved B1 conflict. |
| B3 DAUq | 🔴 | Average-type metric; cumulative pacing is wrong. Goal exists in `dauq_actuals_pacing_current.py` (131.4M) but tab renders `grey`/None. Plus latent defect **D1**: `dauq` strategy compares an absolute goal against `>= 1`, so any real DAUq goal renders **permanently Green**. |
| B4 Cost A/B metrics | 🔴 | Direction never established. "Aggressive = ×1.2 momentum" sets a **worse** CPA goal. Affects 4 of 9 A/B metrics. |
| B5 Marketplace Efficiency `>=25x` | 🔴 | Floor goal must populate `target_lower_bound`, not `target_value`. Step 4 offers non-existent `floor_only`; real rule is `lower_bounded_goal`. |
| B6 Tier0 Availability 99.90% | 🔴 | Relative bands are dangerous: 98% of a 99.90% goal = 97.9% availability graded **Green**. Needs an absolute error budget; no strategy provides one (**D4**). |
| B7 Revenue/FTE | 🔴 | Goal-only (`qtd = 'TBD'`). FY $3.7M exceeds every quarterly goal because it's an **LTM level, not a sum** — a metric type Step 1's menu lacks. Q4 unset. |
| B8 Shopping Revenue | 🟡 | Only one quarter of a four-quarter ladder recorded; $22M CQ vs $70M FY unverifiable. Hardcoded QTD $5,614,458 is a bespoke weekly shape Step 3 can't reproduce. |
| B9 No goal by design | 🔴 | No path to record the decision. gROAS\*/RFD/Retention keep surfacing as ambiguous "Missing". |
| B10 Thriving Communities | 🔴 | Goal source named ("2026 Community Growth Plan") but not wired. Neither Fast nor Full Path handles an inaccessible source. |
| B11 Retirement | 🔴 | All steps only create. No `effective_to`, no supersede, no change-log entry. |
| B12 % top-200 brand advertisers | 🔴 | No actuals cell exists. Step 1 cannot start; no way to register goal intent. |
| B13 Label drift | 🔴 | Goals keyed on display name. Reproduces the Post-Install CPA blank-goal bug. Tracker still lists retired CVR/IIR/CPI A/B. |
| B14 Batch quarterly lock | 🔴 | Single-metric, single-session. Real job is 15 metrics × 9 owners. No progress tracking; orchestrator state is fictional. |

**Score: 1 of 17 cases clean (A2). 4 partial. 12 fail.**

---

## Part 3 — Per-skill scorecard

| Skill | Gets right | Needs context | Verdict |
|---|---|---|---|
| **Orchestrator** | Routing table; artifact-linking rules | State persistence is fictional; references a template that doesn't exist; no batch mode | **Rewrite** |
| **Step 1 Topographer** | Fast Path; partial-quarter QTD rule (81-pt correction); data health; metric-type menu | Quarter length; within-quarter shape; seasonality thresholds miscalibrated; mandatory sMAPE often infeasible | **Trim hard, keep the core** |
| **Step 2 Architect** | Ambition framework; declining-segment reframe; sanity checks | No top-down route; unjustified multipliers anti-correlated with the right answer on decelerating metrics; no direction | **Add Route A; make multipliers advisory** |
| **Step 3 Pacer** | Point-in-time vs cumulative ratio distinction; effort curve | No shape algorithm; ignores production `previous_quarter_exit`; linear default measurably wrong | **Expand — highest leverage** |
| **Step 4 Signaler** | Volatility reasoning; √time rationale | Every policy ID fictional; narrowing bands unimplementable; duplicates registry data | **Replace with registry lookup** |
| **Step 5 Publisher** | — | Target storage doesn't exist; no ID, owner, approval, or versioning | **Rewrite as registry-native** |

---

## Part 4 — Decisions only Yoni can make

Extracted from every 🔴 above. These are **business decisions**, deliberately not resolved:

| # | Decision | Evidence | Blocks |
|---|---|---|---|
| **1** | **Which impressions goal is canonical — 117.70B or 112.33B?** Recommend 117.70B; 112.33B implies −1.43% QoQ on a metric that grew 9 of 10 quarters. Needs Finance (Yona) confirmation. | Live run §5 | B1, and eCPM (B2) which is blocked on it |
| **2** | **Is 117.70B (+12.52% YoY) the intended ambition** when run rate implies 121.56B (+16.21%)? Deceleration argues the conservative number is right — but that should be explicit, not implicit. | Live run §5 | Whether Q3 is sandbagged |
| **3** | **Should pacing use linear or prior-year seasonal shape?** 3.90pp difference — larger than the whole Yellow band. Linear risks false Yellow alarms on back-loaded metrics. | Live run §5 | All cumulative metrics |
| **4** | **Do we build a real goal store, or is the governance Sheet it?** Determines whether Step 5 writes to the Google Sheet Goal Registry or a warehouse table. Open question §8.1 of the architecture doc. | Step 5 eval | Automation feasibility |
| **5** | **Should narrowing bands be built, or dropped from the method?** Currently taught but unimplementable. | Step 4 eval, D5 | Step 4 scope |
| **6** | **Who owns `CANONICAL_METRIC_MAP` / the alias map?** Architecture doc open question §8.2. Without an owner, label drift (B13) recurs. | B13 | Goal-key stability |
| **7** | **Are Scale Our Foundations + Revenue/FTE getting actuals pipelines, or should they be marked `no_actuals_pipeline` permanently?** Architecture doc §8.3. | B7, B12 | 5 metrics' goal status |
| **8** | **Is `Missing` acceptable for `No goal by design` metrics until a path exists?** Affects 3 metrics' dashboard credibility. | B9 | Trust in RAG |
| **9** | **Fix defect D1 before wiring any DAUq goal?** As-is, a real DAUq goal renders permanently Green on a Tier 0 metric. | D1 | DAUq goal-setting |
| **10** | **What's the quarterly lock date and escalation path** for 15 metrics × 9 owners? | B14 | Whether batch mode helps |

---

## Headline

The analytical content is better than the scaffolding around it. Two Step 1 rules (Fast Path,
partial-quarter QTD) and two Step 2 rules (ambition framing, declining-segment reframe) are
genuinely valuable and were validated live.

But the workflow **fails at the ends, not the middle**. It cannot tell whether a goal already
exists (Step 0 missing), and it cannot store one when it's done (Step 5 broken). On the live case
it would have invented a third conflicting number and had nowhere to put it. That is why goals are
still Python literals — and it's what [Deliverable 4](04_IMPROVEMENTS.md) fixes first.
