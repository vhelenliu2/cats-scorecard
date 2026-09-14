# Deliverable 1 — Goaling Skill Inventory

> Baseline audited: `goal-skills.zip` (6 skills, 1,912 lines), installed unmodified at
> [`.cursor/skills/`](../../.cursor/skills/) so improvements are diffable against it.

## 1. What exists

| # | Skill | Lines | Stated output | Maturity |
|---|-------|------:|---------------|----------|
| — | [goal-workflow-orchestrator](../../.cursor/skills/goal-workflow-orchestrator/SKILL.md) | 159 | Routing + progress tracking | Usable |
| 1 | [goal-step1-topographer](../../.cursor/skills/goal-step1-topographer/SKILL.md) | 945 | Insight Card, cleaned data, segmentation | Over-built |
| 2 | [goal-step2-architect](../../.cursor/skills/goal-step2-architect/SKILL.md) | 402 | Goal value + rationale | Strong |
| 3 | [goal-step3-pacer](../../.cursor/skills/goal-step3-pacer/SKILL.md) | 146 | Daily pacing CSV | Thin |
| 4 | [goal-step4-signaler](../../.cursor/skills/goal-step4-signaler/SKILL.md) | 203 | Red/Yellow/Green policy | Detached from code |
| 5 | [goal-step5-publisher](../../.cursor/skills/goal-step5-publisher/SKILL.md) | 57 | BigQuery write + deliverable | Non-functional |

**The weight is inverted.** 49% of the instruction budget goes to Step 1 (analysis — the part a
DS already does well), and 3% goes to Step 5 (persistence and approval — the part that is
actually broken and the entire reason the process is fragmented).

## 2. Prompts, examples, and reusable assets that exist

Worth keeping — this is real intellectual property, not scaffolding:

| Asset | Location | Why it's good |
|-------|----------|---------------|
| Metric type menu (6 types, plain-English + "goal sounds like") | Step 1, §1.0a | Correctly separates Total / Average / Snapshot / Rolling / Ratio / Progress-to-ceiling. This distinction drives everything downstream. |
| Fast Path detection (table + metric + segmentation ⇒ skip discovery) | Step 1, §"Fast Path" | Right instinct: most stakeholders already know their metric. |
| Partial-quarter QTD like-for-like rules + anti-patterns | Step 1, §1.4 | The `+27% vs +66%` worked example is the single most reusable teaching device in the set. |
| Consolidation patterns for high-cardinality columns | Step 1, §1.1 | `location_country → US vs ROW` matches how this org actually segments. |
| Ambition framework (Realistic / Moderate / Stretch / Stabilize / Turnaround) | Step 2, §"Goal Ambition Framework" | Names the conversation stakeholders actually need to have. |
| **Declining-segment reframe** | Step 2, §"Reframing for Declining Segments" | Genuinely excellent. Catches that "aggressive momentum" on a declining metric means *more decline*, which is not a goal. |
| Momentum snapshot block with trend glyphs | Step 2 | Gives instant intuition before numbers. |
| Point-in-time vs cumulative ratio distinction | Step 3, §3.0a | Correct and non-obvious. eCPM/CTR genuinely need effort curves; MAA adoption does not. |
| Effort curve formula | Step 3, §3.4 | `(Goal × Total_denom − Locked_num) / Remaining_denom` is right. |
| Narrowing-band rationale (√time variance) | Step 4, §4.2 | Sound justification for why tolerance should tighten. |
| Transparency rules (no hidden assumptions, cite context sources) | Step 1, §"Agent Transparency" | Directly addresses the trust problem with agent-set goals. |

## 3. Gaps

### 3.1 Blocking — the workflow cannot complete as written

**G1. Step 5 targets storage that does not exist.** The Publisher writes to BigQuery
`goals_log` and `goal_pacing_daily` and cites `sql/schema_goals.sql`. None of the three exist
anywhere in this repo or the warehouse. Every run of this workflow dead-ends at the final step,
which is precisely why goals still live in Python literals and ad-hoc sheets.

**G2. Step 4's policy IDs are invented.** Not one of the 13 policy IDs in the Signaler exists in
the codebase. A stakeholder who completes Step 4 has selected a policy that cannot be
implemented.

| Step 4 claims | Actually implemented in `status_strategies.py` |
|---|---|
| `pacing_standard`, `pacing_tight`, `pacing_relaxed`, `pacing_with_buffer` | `goal`, `goal_rev`, `goal_rev_2m`, `goal_rev_5m`, `goal_binary` |
| `adoption` | `qtd_goal_product_adoption` |
| `level_dauq` | `dauq` |
| `impressions` | `impressions_pacing` |
| `bounded_range`, `floor_only`, `ceiling_only` | `bounded_goal`, `lower_bounded_goal` |
| `trend_yoy`, `trend_both`, `stabilization` | `qoq`, `yoy`, `both`, `both_1`, `both_point_1` |
| `seasonal`, `segment_weighted`, `leading_indicator`, `conditional` | *(nothing — do not offer these)* |
| — | `shopping_pace`, `qtd_vs_current_q_goal`, `ab_goal`, `value`, `qtd_pacing`, `qtd_goal`, `grey` *(exist but are never offered)* |

Also: **narrowing bands do not exist in production.** Every implemented policy uses static
thresholds. Step 4 spends its most detailed section teaching a mechanic the platform can't honor.

**G3. Four referenced files are missing.** `docs/TRAFFIC_SIGNALING_GUIDE.md` (cited twice by
Step 4), `docs/Goal_Setting_Deliverable_Template.md` (cited by the orchestrator as a mandatory
per-step update), `sql/schema_goals.sql`, and the BQ tables from G1.

**G4. No `metric_id` anywhere.** [`DASHBOARD_WARNING_CONTRACT.md`](../../governance/DASHBOARD_WARNING_CONTRACT.md)
requires joining on `metric_id`, never display name — because display-name drift already broke
CVR/IIR/CPI A/B. The skills identify metrics only by free-text name, reproducing the exact
failure mode the governance layer was built to eliminate.

### 3.2 Structural — the skills and the governance system are disconnected halves

The repo already contains the canonical system of record the skills should be feeding:

- [`governance/build_seed.py`](../../governance/build_seed.py) defines a 15-column **Goal
  Registry** (`goal_id`, `metric_id`, `planning_period`, `target_type`, `target_value`,
  `target_lower_bound`, `target_upper_bound`, `baseline_value`, `target_owner_id`,
  `approved_source_id`, `approval_reference`, `approved_at`, `effective_from`, `effective_to`,
  `status`) and an 18-column Metric Registry carrying `goal_policy` and `status_rule`.
- [`governance/MAINTENANCE_RUNBOOK.md`](../../governance/MAINTENANCE_RUNBOOK.md) already defines
  a **quarterly goal lock** ritual.
- [`hex_edits/METRICS_DATA_ARCHITECTURE.md`](../../hex_edits/METRICS_DATA_ARCHITECTURE.md) §5.3
  already specifies the append-only `goals_history` change log.

**No skill mentions any of it.** The skills produce `docs/` markdown and `data/` CSVs; the
governance layer expects registry rows keyed by `metric_id`. Nothing bridges them. This is the
root cause of the fragmentation the project is trying to fix — the goal-*setting* workflow and
the goal-*storage* contract were designed independently.

Evidence of the cost: all 15 company-level Goal Registry rows are empty stubs
(`target_type = "Owner confirmation required"`, blank `target_value`,
`status ∈ {Needs value migration, Missing}`).

### 3.3 Coverage — the skills only handle one of five real goal shapes

The workflow assumes every goal is **bottom-up derived from history**. In practice, of the ~34
registry metrics:

| Real shape | Example metrics | Skill support |
|---|---|---|
| Bottom-up from history | MAA, Thriving Communities | ✅ Supported |
| **Top-down committed** (Finance/board hands you the number; job is allocation + validation, not derivation) | Ad Impressions, Ads Realized Revenue, Upper Funnel, Measured Revenue | ❌ None. Step 2 would "derive" a number that conflicts with the committed one. |
| **Derived / dependent** (no independent goal possible until parents land) | eCPM (= revenue ÷ impressions) | ❌ None. Step 1 would run a cardinality scan and sMAPE on a metric that has no independent series. |
| **No goal by design** (an explicit, valid registry state) | gROAS\*, Reach/Frequency/Depth, Retention 28D | ❌ None. No path to record this decision, so these keep surfacing as ambiguous "Missing". |
| **Goal-only / no actuals pipeline** | Revenue/FTE, all 4 Scale Our Foundations | ❌ None. Step 1 requires historical data these metrics don't have. |

Top-down is the *most common* case among Tier 0/1 metrics and is completely unsupported.

### 3.4 Process — the stakeholder-facing promises aren't kept

**G5. No owner or approver is ever captured.** The architecture doc names the core failure as
*"no audit trail beyond this chat transcript of who asked for what value and when — if the wrong
number ships, there's no diff to point at."* The Goal Registry has `target_owner_id`,
`approved_source_id`, `approval_reference`, `approved_at` for exactly this. No skill collects any
of them. The workflow reproduces the untraceable-goal problem it was built to solve.

**G6. Single-metric only.** The real job is a quarterly lock across 15+ metrics with different
owners. There is no batch mode, no per-metric status tracking, and no "which metrics still need
goals" view — so the coordination work (the actual bottleneck) stays manual.

**G7. Orchestrator state is fictional.** It instructs the agent to "keep track of where you are"
with no persistence file, and to update a deliverable template that doesn't exist. Across a
multi-session quarterly lock, progress is lost.

**G8. Stakeholder burden is understated.** The user's goal is *"stakeholders don't need to do
much."* As written, the workflow has **17 decision gates** requiring stakeholder input across
5 steps. Many are decisions the stakeholder cannot answer (sMAPE tradeoffs, band widths) or that
should be defaulted from the registry (`status_rule` is already recorded per metric).

### 3.5 Internal consistency

**G9. Broken cross-references.** Step 2 twice cites *"Segmentation Advisor output from
Topographer (Step 1.6)"*; Step 1 has no §1.6 — the artifact is produced at §1.1c.

**G10. Step 1 has three overlapping segmentation sections.** §1.1 (discovery), §1.1b (business-
first selection), §1.2 (selection again, "informed by 1.1b"). §1.1b and §1.2 both ask the user to
pick segments with near-identical prompts. At 945 lines with duplicated instructions, adherence
degrades and the agent picks whichever section it read last.

**G11. Mandatory sMAPE is wrong for most metrics here.** Step 1's checklist marks the sMAPE
backtest **MANDATORY**, but it's meaningless for derived metrics (eCPM), goal-only metrics (Scale
Foundations), metrics with <1yr history, and top-down committed metrics where segmentation is
dictated by org structure rather than forecast accuracy. Marking it mandatory trains the agent to
produce a number that looks rigorous and isn't.

**G12. Step 3 ignores production pacing math.** Production computes the QTD goal as a linear ramp
from `previous_quarter_exit` toward `current_quarter_goal`
([`status_and_metric.py:534-544`](../../hex_edits/modules/status_and_metric.py)). Step 3 never
mentions `previous_quarter_exit` — so its pacing curve won't match what the dashboard displays,
and a goal set via the skill will show a different RAG status than the skill predicted.

## 4. Summary

| Category | Count | Severity |
|---|---|---|
| Blocking defects (workflow cannot complete) | G1–G4 | **P0** |
| Missing governance integration | §3.2 | **P0** |
| Unsupported goal shapes | 4 of 5 | **P0** |
| Missing audit/approval capture | G5 | **P1** |
| No batch mode for quarterly lock | G6 | **P1** |
| Stakeholder burden (17 gates) | G8 | **P1** |
| Internal inconsistency / bloat | G9–G12 | **P2** |

**Headline:** the analytical thinking in these skills is good and worth preserving. What's
missing is the half that makes goaling *standardized* — a canonical destination, a stable metric
key, captured approval, and paths for the goal shapes that dominate this metric set. The next
deliverable tests these gaps against real cases rather than asserting them.
