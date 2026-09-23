# Ingest pilot state

_Updated: 2026-09-23_

- Last run: `fixture` self-test (no credentials, no live sheet pull)
- As-of: `2026-09-01`
- Result: **OK** — publish-ready **5** · held for review **5**
- Held rows are the MAA LCS/MM/SMB and DAUq US/ROW segments, which stay in
  review until they have Metric Registry rows. This is expected, not a failure.

No live `--mode gsheet` run has been recorded yet. Run artifacts land in
`docs/ingestion/runs/<timestamp>/` and are not tracked in git.
