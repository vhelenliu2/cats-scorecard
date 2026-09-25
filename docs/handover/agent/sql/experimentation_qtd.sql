-- Experimentation Velocity — QTD distinct Ads experiments.
-- READ-ONLY. Confirm table/column names with the Scale team before enabling.
-- Contract expected by calculations/experimentation_velocity.py:
--   columns: experiment_id, start_date (DATE), unique_objects (NUMERIC)
-- The calc filters unique_objects > 1000 and QTD window in Python, but keeping
-- the filters here too reduces scan cost.
--
-- TODO_CONFIRM: replace <project.dataset.table> with the approved source.
SELECT
  experiment_id,
  start_date,
  unique_objects
FROM `TODO_CONFIRM_project.dataset.ads_experiments`
WHERE unique_objects > 1000
  AND start_date >= DATE_TRUNC(CURRENT_DATE(), QUARTER)
  AND start_date <= CURRENT_DATE()
