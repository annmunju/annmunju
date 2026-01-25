-- 실험 시작/끝 시간을 실험 시간으로 바꿔 넣기
SET START_TS = '2026-01-08 12:00:00'::timestamp_ntz;
SET END_TS   = '2026-01-08 14:00:00'::timestamp_ntz;

SELECT
  warehouse_name,
  SUM(credits_used)          AS credits_used_total,
  SUM(credits_used_cloud_services) AS credits_used_cloud_services,
  MIN(start_time) AS min_start_time,
  MAX(end_time)   AS max_end_time
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE warehouse_name = 'SNOWFLAKE_LEARNING_WH'
  AND start_time >= $START_TS
  AND end_time   <= $END_TS
GROUP BY 1;