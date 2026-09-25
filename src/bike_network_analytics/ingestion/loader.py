"""Raw and processed data loaders. Never hardcode data paths outside this module."""

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = REPO_ROOT / "data" / "raw"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"


def load_raw_daily_hires() -> pd.DataFrame:
    return pd.read_csv(RAW_DIR / "tfl_daily_cycle_hires.csv", parse_dates=["date"])


def load_raw_holidays() -> pd.DataFrame:
    return pd.read_csv(RAW_DIR / "england_public_holidays.csv")


def load_raw_weather() -> pd.DataFrame:
    return pd.read_csv(RAW_DIR / "london_daily_weather.csv", parse_dates=["date"])


def load_processed_dataset() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED_DIR / "daily_hires_with_holidays.csv", parse_dates=["date"])
    return df.sort_values("date").reset_index(drop=True)
