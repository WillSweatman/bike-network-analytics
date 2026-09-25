const form = document.getElementById("forecast-form");
const dateInput = document.getElementById("date");
const result = document.getElementById("result");
const errorBox = document.getElementById("error");

async function loadDateRange() {
    const response = await fetch("/api/health");
    const health = await response.json();
    dateInput.min = health.min_date;
    dateInput.max = health.max_date;
    dateInput.value = health.max_date;
}

function showError(message) {
    result.hidden = true;
    errorBox.hidden = false;
    errorBox.textContent = message;
}

function showResult(forecast) {
    errorBox.hidden = true;
    result.hidden = false;
    document.getElementById("predicted-hires").textContent = Math.round(
        forecast.predicted_hires
    ).toLocaleString("en-GB");
    document.getElementById("actual-hires").textContent = forecast.actual_hires.toLocaleString(
        "en-GB"
    );
    document.getElementById("temperature").textContent = `${forecast.temperature_c}°C`;
    document.getElementById("precipitation").textContent = `${forecast.precipitation_mm} mm`;
    document.getElementById("weather-condition").textContent = forecast.weather_condition;
    document.getElementById("is-bank-holiday").textContent = forecast.is_bank_holiday
        ? "Yes"
        : "No";
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const response = await fetch(`/api/forecast?date=${dateInput.value}`);
    const body = await response.json();
    if (!response.ok) {
        showError(body.detail);
        return;
    }
    showResult(body);
});

loadDateRange();
