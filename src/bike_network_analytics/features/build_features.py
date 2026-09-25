import pandas as pd

from bike_network_analytics.ingestion.loader import (
    PROCESSED_DIR,
    load_processed_dataset,
    load_raw_daily_hires,
    load_raw_holidays,
    load_raw_weather,
)

DATE_FEATURE_COLUMNS = [
    "day_of_week",
    "month",
    "year",
    "is_bank_holiday",
    "lag_1",
    "lag_7",
    "lag_28",
    "rolling_mean_7",
    "rolling_mean_28",
]
WEATHER_FEATURE_COLUMNS = ["temperature_c", "precipitation_mm"]
FEATURE_COLUMNS = DATE_FEATURE_COLUMNS + WEATHER_FEATURE_COLUMNS
TARGET_COLUMN = "cycle_hire_count"


def _tidy_holidays(holidays_raw: pd.DataFrame) -> pd.DataFrame:
    holidays = holidays_raw.copy()
    holidays["date"] = pd.to_datetime(holidays["Formatted Date"], format="%d %B %Y")
    return holidays.rename(columns={"Bank Holiday": "bank_holiday_name"})[
        ["date", "bank_holiday_name"]
    ]


def _tidy_weather(weather_raw: pd.DataFrame) -> pd.DataFrame:
    return weather_raw.rename(
        columns={
            "temperature_2m_mean": "temperature_c",
            "precipitation_sum": "precipitation_mm",
        }
    )[["date", "temperature_c", "precipitation_mm", "weather_condition"]]


def build_processed_dataset() -> pd.DataFrame:
    """Mirrors notebook 01's join and calendar/lag/rolling feature engineering."""
    hires = load_raw_daily_hires()
    holidays = _tidy_holidays(load_raw_holidays())
    weather = _tidy_weather(load_raw_weather())

    df = hires.merge(holidays, on="date", how="left").merge(weather, on="date", how="left")
    df["is_bank_holiday"] = df["bank_holiday_name"].notna()
    df = df.rename(columns={"number_of_bicycle_hires": TARGET_COLUMN})

    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year

    # shift(1) first so a row never sees its own day's count
    df["lag_1"] = df[TARGET_COLUMN].shift(1)
    df["lag_7"] = df[TARGET_COLUMN].shift(7)
    df["lag_28"] = df[TARGET_COLUMN].shift(28)
    df["rolling_mean_7"] = df[TARGET_COLUMN].shift(1).rolling(7).mean()
    df["rolling_mean_28"] = df[TARGET_COLUMN].shift(1).rolling(28).mean()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DIR / "daily_hires_with_holidays.csv", index=False)
    return df


def build_inference_row(target_date: pd.Timestamp) -> pd.DataFrame:
    """Full processed-dataset row for a date already covered by history (region A only, for now).

    Includes display fields (weather_condition, etc.) alongside FEATURE_COLUMNS - callers doing
    inference should select `row[FEATURE_COLUMNS]` before passing it to a model.
    """
    df = load_processed_dataset()
    row = df.loc[df["date"] == pd.Timestamp(target_date)]
    if row.empty:
        raise ValueError(
            f"No processed data for {target_date.date()}; date is outside known history."
        )
    return row
