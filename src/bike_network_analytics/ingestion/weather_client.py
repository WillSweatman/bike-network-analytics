import datetime as dt

import httpx
import pandas as pd

LATITUDE = 51.5074
LONGITUDE = -0.1278
TIMEZONE = "Europe/London"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
DAILY_FIELDS = "temperature_2m_mean,precipitation_sum,weather_code"

# WMO weather codes actually seen in this project's data (see data/raw/london_daily_weather.csv).
WMO_WEATHER_CONDITIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
}


def _parse_daily_response(payload: dict) -> pd.DataFrame:
    """Shared by both APIs — archive and forecast responses use the same daily field names/units."""
    daily = payload["daily"]
    return pd.DataFrame(
        {
            "date": pd.to_datetime(daily["time"]),
            "temperature_c": daily["temperature_2m_mean"],
            "precipitation_mm": daily["precipitation_sum"],
            "weather_condition": [
                WMO_WEATHER_CONDITIONS.get(code, "Unknown") for code in daily["weather_code"]
            ],
        }
    )


def _fetch(url: str, start: dt.date, end: dt.date) -> pd.DataFrame:
    response = httpx.get(
        url,
        params={
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "daily": DAILY_FIELDS,
            "timezone": TIMEZONE,
        },
        timeout=15,
    )
    response.raise_for_status()
    return _parse_daily_response(response.json())


def fetch_historical_weather(start: dt.date, end: dt.date) -> pd.DataFrame:
    """Actual observed daily weather for London (Open-Meteo archive API)."""
    return _fetch(ARCHIVE_URL, start, end)


def fetch_forecast_weather(start: dt.date, end: dt.date) -> pd.DataFrame:
    """Forecast daily weather for London (Open-Meteo forecast API, ~16-day horizon)."""
    return _fetch(FORECAST_URL, start, end)
