import datetime as dt
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from bike_network_analytics.api.schemas import (
    ForecastResponse,
    HealthResponse,
    MetricsResponse,
    ModelMetrics,
)
from bike_network_analytics.evaluation.metrics import compute_metrics, test_date_range
from bike_network_analytics.features.build_features import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    build_inference_row,
)
from bike_network_analytics.models.inference import load_model, predict

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Bike Network Analytics")

_model = load_model("v0.2")
_metrics = compute_metrics()
# Bounding the API to the test range only (not the full known history) is deliberate: dates
# before this were used to train v0.2, so "predicting" them would just replay training data.
_test_start_date, _test_end_date = test_date_range()


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        min_date=_test_start_date.date(),
        max_date=_test_end_date.date(),
    )


@app.get("/api/forecast", response_model=ForecastResponse)
def forecast(date: dt.date | None = None) -> ForecastResponse:
    # Phase 1 only covers region A, so default to the most recent known date rather than
    # "tomorrow" - Phase 2 restores a forward-looking default once regions B/C exist.
    target_date = pd.Timestamp(date) if date is not None else _test_end_date

    if not (_test_start_date <= target_date <= _test_end_date):
        raise HTTPException(
            status_code=400,
            detail=(
                f"{date} is outside the test period "
                f"({_test_start_date.date()} to {_test_end_date.date()}); "
                "earlier dates were used to train v0.2, later dates aren't known yet."
            ),
        )

    try:
        row = build_inference_row(target_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    predicted_hires = predict(_model, row[FEATURE_COLUMNS])

    return ForecastResponse(
        date=target_date.date(),
        predicted_hires=predicted_hires,
        actual_hires=int(row[TARGET_COLUMN].iloc[0]),
        temperature_c=float(row["temperature_c"].iloc[0]),
        precipitation_mm=float(row["precipitation_mm"].iloc[0]),
        weather_condition=str(row["weather_condition"].iloc[0]),
        is_bank_holiday=bool(row["is_bank_holiday"].iloc[0]),
    )


@app.get("/api/metrics", response_model=MetricsResponse)
def metrics() -> MetricsResponse:
    return MetricsResponse(
        models={version: ModelMetrics(**values) for version, values in _metrics.items()}
    )


# Mounted last so it never shadows the /api/* routes above.
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
