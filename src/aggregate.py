# src/aggregate.py
from google.cloud import bigquery
import config

SUMMARY_SQL = """
CREATE OR REPLACE TABLE `{project}.{dataset}.{summary}` AS
WITH home AS (
  SELECT
    Season,
    HomeTeam AS Team,
    1 AS Played,
    CAST(FTHG AS INT64) AS GF,
    CAST(FTAG AS INT64) AS GA,
    CASE FTR WHEN 'H' THEN 1 ELSE 0 END AS Win,
    CASE FTR WHEN 'D' THEN 1 ELSE 0 END AS Draw,
    CASE FTR WHEN 'A' THEN 1 ELSE 0 END AS Loss
  FROM `{project}.{dataset}.{raw}`
  WHERE HomeTeam IS NOT NULL AND FTR IS NOT NULL
),
away AS (
  SELECT
    Season,
    AwayTeam AS Team,
    1 AS Played,
    CAST(FTAG AS INT64) AS GF,
    CAST(FTHG AS INT64) AS GA,
    CASE FTR WHEN 'A' THEN 1 ELSE 0 END AS Win,
    CASE FTR WHEN 'D' THEN 1 ELSE 0 END AS Draw,
    CASE FTR WHEN 'H' THEN 1 ELSE 0 END AS Loss
  FROM `{project}.{dataset}.{raw}`
  WHERE AwayTeam IS NOT NULL AND FTR IS NOT NULL
),
combined AS (
  SELECT * FROM home
  UNION ALL
  SELECT * FROM away
)
SELECT
  Season,
  Team,
  SUM(Played)                     AS Played,
  SUM(Win)                        AS Wins,
  SUM(Draw)                       AS Draws,
  SUM(Loss)                       AS Losses,
  SUM(GF)                         AS GoalsFor,
  SUM(GA)                         AS GoalsAgainst,
  SUM(GF) - SUM(GA)               AS GoalDifference,
  SUM(Win) * 3 + SUM(Draw)        AS Points
FROM combined
GROUP BY Season, Team
ORDER BY Season, Points DESC
"""


def build_summary(client: bigquery.Client) -> None:
    sql = SUMMARY_SQL.format(
        project=config.PROJECT_ID,
        dataset=config.DATASET_ID,
        summary=config.SUMMARY_TABLE,
        raw=config.RAW_TABLE,
    )
    job = client.query(sql, location=config.LOCATION)
    job.result()
    table_id = f"{config.PROJECT_ID}.{config.DATASET_ID}.{config.SUMMARY_TABLE}"
    table = client.get_table(table_id)
    print(f"summary built: {table.num_rows} rows into {table_id}")


if __name__ == "__main__":
    from src.load_bq import get_client
    build_summary(get_client())