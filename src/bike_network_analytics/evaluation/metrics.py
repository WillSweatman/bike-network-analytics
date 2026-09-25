import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from bike_network_analytics.features.build_features import (
    DATE_FEATURE_COLUMNS,
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    build_processed_dataset,
)
from bike_network_analytics.models.inference import load_model

# v0.1 was trained on date features only; v0.2 adds weather - see notebook 03
MODEL_FEATURE_COLUMNS = {
    "v0.1": DATE_FEATURE_COLUMNS,
    "v0.2": FEATURE_COLUMNS,
}


def _cleaned_dataset() -> pd.DataFrame:
    df = build_processed_dataset()
    return df.dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN]).reset_index(drop=True)


def _chronological_test_split(df: pd.DataFrame) -> pd.DataFrame:
    split_index = int(len(df) * 0.8)
    return df.iloc[split_index:]


def test_date_range() -> tuple[pd.Timestamp, pd.Timestamp]:
    """Start/end dates of the chronological test split - the only dates v0.2 wasn't trained on."""
    test_df = _chronological_test_split(_cleaned_dataset())
    return test_df["date"].min(), test_df["date"].max()


def compute_metrics() -> dict[str, dict]:
    """MAE/RMSE/R2 for each trained model, on the shared chronological test split."""
    test_df = _chronological_test_split(_cleaned_dataset())
    y_test = test_df[TARGET_COLUMN]

    results = {}
    for version, feature_columns in MODEL_FEATURE_COLUMNS.items():
        model = load_model(version)
        predictions = model.predict(test_df[feature_columns])
        importances = pd.Series(model.feature_importances_, index=feature_columns).sort_values(
            ascending=False
        )
        results[version] = {
            "mae": mean_absolute_error(y_test, predictions),
            "rmse": np.sqrt(mean_squared_error(y_test, predictions)),
            "r2": r2_score(y_test, predictions),
            "feature_importances": importances.to_dict(),
        }
    return results
