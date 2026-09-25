-- Revenue (monthly) for Revenue / S+M FTE.
-- READ-ONLY. Confirm table/column names with the revenue warehouse owner.
-- Contract expected by calculations/revenue_fte.py:
--   columns: month ('YYYY-MM' or DATE truncated to month), revenue (NUMERIC)
--
-- TODO_CONFIRM: replace <project.dataset.table> with the approved source.
SELECT
  FORMAT_DATE('%Y-%m', DATE_TRUNC(activity_date, MONTH)) AS month,
  SUM(revenue) AS revenue
FROM `TODO_CONFIRM_project.dataset.ads_revenue`
GROUP BY month
ORDER BY month
