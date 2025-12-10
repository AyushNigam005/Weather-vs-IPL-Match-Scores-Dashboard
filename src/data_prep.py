# src/data_prep.py

from pathlib import Path
from dateutil import parser
import pandas as pd


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def parse_date_safe(date_str):
    """
    Safely parse a date string into YYYY-MM-DD.
    Assumes Indian-style or ISO dates.
    """
    try:
        return parser.parse(str(date_str)).date()
    except Exception:
        return None


def load_ipl_data(filename: str = "ipl_matches_sample.csv") -> pd.DataFrame:
    path = DATA_DIR / filename
    df = pd.read_csv(path)

    # Standardize column names (lowercase)
    df.columns = [c.strip().lower() for c in df.columns]

    # Ensure required columns exist
    required_cols = {"date", "city", "total_runs"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required IPL columns: {missing}")

    # Parse date
    df["date"] = df["date"].apply(parse_date_safe)
    df = df.dropna(subset=["date"])

    # Ensure city is string
    df["city"] = df["city"].astype(str).str.strip()

    # Optional: clean season as string
    if "season" in df.columns:
        df["season"] = df["season"].astype(str)

    return df


def load_weather_data(filename: str = "weather_sample.csv") -> pd.DataFrame:
    path = DATA_DIR / filename
    df = pd.read_csv(path)

    df.columns = [c.strip().lower() for c in df.columns]

    required_cols = {"date", "city", "temp_c"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required Weather columns: {missing}")

    df["date"] = df["date"].apply(parse_date_safe)
    df = df.dropna(subset=["date"])

    df["city"] = df["city"].astype(str).str.strip()

    # Fill missing optional columns if not present
    if "humidity" not in df.columns:
        df["humidity"] = None
    if "weather_type" not in df.columns:
        df["weather_type"] = "Unknown"

    return df


def merge_ipl_weather(
    ipl_df: pd.DataFrame,
    weather_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge IPL and weather on (date, city).
    If your real data is different, adjust join keys here.
    """
    merged = pd.merge(
        ipl_df,
        weather_df,
        on=["date", "city"],
        how="inner",
        suffixes=("_match", "_weather"),
    )

    # Create helper columns
    merged["date_str"] = merged["date"].astype(str)

    # Weather buckets
    merged["temp_bucket"] = pd.cut(
        merged["temp_c"],
        bins=[0, 25, 30, 35, 100],
        labels=["Cool (<=25)", "Warm (26-30)", "Hot (31-35)", "Very Hot (>35)"],
        include_lowest=True,
    )

    return merged


def load_and_prepare():
    ipl_df = load_ipl_data()
    weather_df = load_weather_data()
    merged_df = merge_ipl_weather(ipl_df, weather_df)
    return merged_df


if __name__ == "__main__":
    df = load_and_prepare()
    print(df.head())
    print(f"Rows after merge: {len(df)}")
