# scripts/run_pipeline.py
from src.ingest import build_dataframe
from src.aggregate import build_summary
from src.load_bq import get_client, ensure_dataset, load_matches


def main():
    print("building dataframe (all seasons)...")
    df = build_dataframe(start_year=1993, end_year=2026)
    print(f"combined shape: {df.shape}")

    client = get_client()
    ensure_dataset(client)
    load_matches(df, client)
    build_summary(client)
    print("done.")


if __name__ == "__main__":
    main()