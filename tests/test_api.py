from fastapi.testclient import TestClient

from bike_network_analytics.api.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["min_date"] < body["max_date"]


def test_forecast_default_date() -> None:
    response = client.get("/api/forecast")
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "date",
        "predicted_hires",
        "actual_hires",
        "temperature_c",
        "precipitation_mm",
        "weather_condition",
        "is_bank_holiday",
    }


def test_forecast_known_historical_date() -> None:
    response = client.get("/api/forecast", params={"date": "2026-08-15"})
    assert response.status_code == 200
    body = response.json()
    assert body["date"] == "2026-08-15"
    assert body["actual_hires"] == 25768


def test_forecast_rejects_date_beyond_test_period() -> None:
    response = client.get("/api/forecast", params={"date": "2030-01-01"})
    assert response.status_code == 400
    assert "outside the test period" in response.json()["detail"]


def test_forecast_rejects_training_range_date() -> None:
    """Dates before the test split were used to train v0.2, so they must also be rejected."""
    response = client.get("/api/forecast", params={"date": "2015-01-01"})
    assert response.status_code == 400
    assert "outside the test period" in response.json()["detail"]


def test_metrics() -> None:
    response = client.get("/api/metrics")
    assert response.status_code == 200
    body = response.json()["models"]
    assert set(body) == {"v0.1", "v0.2"}
    assert body["v0.2"]["mae"] < body["v0.1"]["mae"]


def test_static_frontend_served_at_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_api_routes_are_not_shadowed_by_the_static_mount() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
