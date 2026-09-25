from pathlib import Path

import pandas as pd
from xgboost import XGBRegressor

REPO_ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR = REPO_ROOT / "models"


def load_model(version: str) -> XGBRegressor:
    model = XGBRegressor()
    model.load_model(MODELS_DIR / f"{version}_xgb.json")
    return model


def predict(model: XGBRegressor, feature_row: pd.DataFrame) -> float:
    return float(model.predict(feature_row)[0])
