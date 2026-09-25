# bike-network-analytics

Forecasting demand for the London Santander Cycle Hire scheme.

## Status

**v0.1** — a baseline daily demand forecast built purely from date-derived
features (day of week, month, year, bank holiday flag, and lags/rolling
means of the hire count itself). An XGBoost model is compared against a
seasonal-naive baseline (predicting the same weekday's count from the
previous week).

**v0.2** — adds London daily weather (temperature, precipitation) as
features. Evaluated against the saved v0.1 model on the same test set:
a 5.8% MAE improvement, though recent hire history (`rolling_mean_7`,
`lag_1`) still dominates feature importance - see `docs/NOTES.md`.

**v0.3** — a local FastAPI app that serves the v0.2 model over HTTP, plus
a small web page to query it. Currently limited to v0.2's chronological
test range (2023-06-19 to 2026-08-31): earlier dates were used to train
the model, later dates aren't known yet. This is a local-only build, not
a public release - see "Versioning" below. See `PLAN.md` for the fuller
roadmap (live weather forecasting, model comparison, etc.).

## Versioning

`v0.1`/`v0.2`/`v0.3` are internal, local-only iterations - each one an
isolated experiment or build compared against the last, not something
handed to anyone outside this repo. **`v1.0` is reserved for the first
hosted version anyone can use without cloning the repo** (Docker + real
deployment, deliberately deferred until then per `AGENTS.md`). Branches
are named descriptively, not by version - the version is applied as a
tag once a branch is merged to `main`.

## Repository structure

```
data/
  raw/          source datasets (committed - small, source of truth)
  processed/    regenerated from raw + code on app startup (not committed)
notebooks/
  01_data_prep.ipynb           joins raw data, engineers features
  02_data_exploration.ipynb    EDA - trend, seasonality, correlations
  03_training_and_modelling.ipynb   baseline vs. XGBoost model
src/bike_network_analytics/
  ingestion/    raw data loaders + live weather/holiday API clients
  features/     feature engineering (mirrors notebook 01)
  models/       model training/inference code (see models/ below for artefacts)
  evaluation/   shared MAE/RMSE/R² + feature-importance computation
  api/          FastAPI app + static frontend
models/         serialised model artefacts (v0.1_xgb.json, v0.2_xgb.json)
tests/          pytest suite
docs/
  NOTES.md      dated log of observations worth remembering
```

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.13+.

```
uv sync
```

## Running the app

```
uv run uvicorn bike_network_analytics.api.main:app --reload
```

Then open <http://localhost:8000> in a browser. The first request regenerates
`data/processed/daily_hires_with_holidays.csv` from the committed raw CSVs
automatically, so no manual data-prep step is needed on a fresh clone.

If you're using VS Code, the same command is available as the **FastAPI**
task (Terminal → Run Task → FastAPI) - it runs in a dedicated Git Bash
terminal.

## Running the tests

```
uv run pytest
```

## Notebooks (historical record)

The v0.1/v0.2 experiments were built and evaluated as notebooks; they're
kept as-is rather than retrofitted to use the `src/` modules, since editing
frozen experiment notebooks conflicts with treating past versions as
historic.

```
uv run python -m ipykernel install --user --name bike-network-analytics
```

Then open the notebooks in order (`01` → `02` → `03`) and select the
`bike-network-analytics` kernel. `01_data_prep.ipynb` must be run first -
it produces `data/processed/daily_hires_with_holidays.csv`, which the
other two notebooks read.