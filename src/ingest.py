
import io
import re
import requests
import pandas as pd
from src.seasons import season_codes

BASE_URL = "https://www.football-data.co.uk/mmz4281/{code}/E0.csv"

# columns that stay text; everything else coerced to numeric
KEEP_STR = {
    "Div", "Date", "Time", "HomeTeam", "AwayTeam",
    "FTR", "HTR", "Referee", "Season", "SeasonCode", "SourceURL",
}

def _season_label(code: str) -> str:
    yy = int(code[:2])
    start = 1900 + yy if yy >= 93 else 2000 + yy
    return f"{start}-{code[2:]}"


def load_season(code: str, session: requests.Session) -> pd.DataFrame | None:
    url = BASE_URL.format(code=code)
    resp = session.get(url, timeout=30)
    if resp.status_code == 404:
        print(f"  skip {code}: not found (404)")
        return None
    resp.raise_for_status()

    df = pd.read_csv(
        io.BytesIO(resp.content),
        encoding="latin-1",       # tolerate non-UTF8 bytes in old files
        on_bad_lines="skip",      # tolerate ragged rows
    )
    # drop stray trailing empty columns (from trailing commas)
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    df = df.dropna(how="all")
    if df.empty:
        return None

    df["Season"] = _season_label(code)
    df["SeasonCode"] = code
    df["SourceURL"] = url
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    return df


def sanitize(col: str) -> str:
    c = col.replace(">", "over_").replace("<", "under_")
    c = c.replace(".", "_").replace(" ", "_").replace("&", "_and_")
    c = re.sub(r"[^0-9a-zA-Z_]", "_", c)
    if c and c[0].isdigit():
        c = "c_" + c
    return c

def build_dataframe(start_year=1993, end_year=2026) -> pd.DataFrame:
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (epl-tutorial)"})

    frames = []
    for code in season_codes(start_year, end_year):
        print(f"downloading {code} ...")
        df = load_season(code, session)
        if df is not None:
            frames.append(df)

    combined = pd.concat(frames, ignore_index=True, sort=False)
    combined.columns = [sanitize(c) for c in combined.columns]

    for c in combined.columns:
        if c not in KEEP_STR:
            combined[c] = pd.to_numeric(combined[c], errors="coerce")

    return combined

if __name__ == "__main__":
    # TEST MODE: just 2 recent seasons, cheap and fast
    df = build_dataframe(start_year=2022, end_year=2024)
    print("\nshape:", df.shape)
    print("seasons:", df["Season"].unique())
    print("columns:", len(df.columns))
    print(df[["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]].head())