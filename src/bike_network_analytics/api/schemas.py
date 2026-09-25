import datetime as dt

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    min_date: dt.date
    max_date: dt.date


class ForecastResponse(BaseModel):
    date: dt.date
    predicted_hires: float
    actual_hires: int
    temperature_c: float
    precipitation_mm: float
    weather_condition: str
    is_bank_holiday: bool


class ModelMetrics(BaseModel):
    mae: float
    rmse: float
    r2: float
    feature_importances: dict[str, float]


class MetricsResponse(BaseModel):
    models: dict[str, ModelMetrics]
