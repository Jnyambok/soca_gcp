# src/load_bq.py
from google.cloud import bigquery
import config


def get_client() -> bigquery.Client:
    # Uses ADC from `gcloud auth application-default login` -- no key file
    return bigquery.Client(project=config.PROJECT_ID, location=config.LOCATION)


def ensure_dataset(client: bigquery.Client) -> None:
    dataset_id = f"{config.PROJECT_ID}.{config.DATASET_ID}"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = config.LOCATION
    client.create_dataset(dataset, exists_ok=True)
    print(f"dataset ready: {dataset_id} ({config.LOCATION})")


def load_matches(df, client: bigquery.Client) -> None:
    table_id = f"{config.PROJECT_ID}.{config.DATASET_ID}.{config.RAW_TABLE}"
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=True,
    )
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()  # wait for completion
    table = client.get_table(table_id)
    print(f"loaded {table.num_rows} rows, {len(table.schema)} columns into {table_id}")