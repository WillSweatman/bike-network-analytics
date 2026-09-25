import pandas as pd
import pytest

from bike_network_analytics.features.build_features import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    build_inference_row,
    build_processed_dataset,
)


@pytest.fixture(scope="module")
def processed_df() -> pd.DataFrame:
    return build_processed_dataset()


def test_lag_1_is_previous_days_count(processed_df: pd.DataFrame) -> None:
    row = processed_df.iloc[100]
    previous_row = processed_df.iloc[99]
    assert row["lag_1"] == previous_row[TARGET_COLUMN]


def test_rolling_mean_7_excludes_current_day(processed_df: pd.DataFrame) -> None:
    row = processed_df.iloc[100]
    window = processed_df[TARGET_COLUMN].iloc[93:100]
    assert row["rolling_mean_7"] == pytest.approx(window.mean())


def test_first_row_has_no_lag_or_rolling_history(processed_df: pd.DataFrame) -> None:
    first_row = processed_df.iloc[0]
    assert first_row[["lag_1", "lag_7", "lag_28", "rolling_mean_7", "rolling_mean_28"]].isna().all()


def test_feature_column_order_matches_training(processed_df: pd.DataFrame) -> None:
    assert list(processed_df[FEATURE_COLUMNS].columns) == FEATURE_COLUMNS


def test_build_inference_row_returns_known_date(processed_df: pd.DataFrame) -> None:
    known_date = processed_df["date"].iloc[-1]
    row = build_inference_row(known_date)
    assert set(FEATURE_COLUMNS).issubset(row.columns)
    assert len(row) == 1


def test_build_inference_row_rejects_unknown_date(processed_df: pd.DataFrame) -> None:
    future_date = processed_df["date"].iloc[-1] + pd.Timedelta(days=365)
    with pytest.raises(ValueError, match="outside known history"):
        build_inference_row(future_date)
