# Notes

## 2026-09-18 - v0.2: recent hire history dominates over weather

The weather-enriched model (`03_training_and_modelling.ipynb`) is still
dominated by `rolling_mean_7` (0.373) and `lag_1` (0.217) - together
~59% of feature importance, versus `precipitation_mm` (0.101) and
`temperature_c` (0.046) at ~15% combined.

Implication for a deployed system: usefully predicting tomorrow's hires
depends far more on having **up-to-date records of the last day and
week's actual hire counts** than on an accurate weather forecast. A
production system needs a reliable feed of recent hire data more urgently
than a weather forecast integration.

## 2026-09-18 - hire data source is monthly, not daily - lag_1 may not be viable live

Checked the actual source: the "Number of Bicycle Hires" dataset on
London Datastore is a single manually-published `tfl-daily-cycle-hires.xls`
file, not a live feed. Its regular publication cadence is **monthly, on
the 8th of each month** - and it's currently running even later than
that, since TfL is mid-migration to a new internal data platform
(Enterprise Data Platform).

This means the most recent *actual* daily count available at any given
time could be weeks to a month stale, not "yesterday." A live system
cannot get `lag_1` or a genuinely current `rolling_mean_7` from this
source. Options if we build a live version:

- Find a more frequent raw feed - checked `cycling.data.tfl.gov.uk`'s
  `usage-stats/` folder (raw per-journey extracts). **Ruled out**: it's
  published in ~2-week chunks but with a multi-month practical backlog
  - the most recent file (as of checking) covered up to 31 May 2026,
  uploaded 6 June 2026, over 3 months stale. Similar order-of-magnitude
  lag to the monthly aggregate file, just a different publishing pattern.
- Otherwise, redefine the lags to match real availability (e.g.
  `lag_30`+) and accept a much longer effective prediction horizon -
  this is a different, likely harder problem than "predict tomorrow."

**Follow-up (confirmed):** TfL's Unified API (`api.tfl.gov.uk`) has a
`/BikePoint` endpoint giving live status (bikes available, empty docks,
total docks) for all ~800 docking stations, refreshed in real time -
free API key required. This is the real data source for the future
station-level phases (station-level forecasting, empty/full station
prediction). It could also be a path to a live daily aggregate for v1,
but it only gives point-in-time occupancy snapshots, not a ready-made
"hires today" total - deriving that would mean polling repeatedly and
inferring trip counts from bike-count changes at each station over
time, which approximates but doesn't exactly match TfL's official
published metric. Real engineering work, not just a data source swap.

Across everything checked, `/BikePoint` is the only genuinely real-time
source found so far - both historical hire datasets (aggregate and raw
per-journey) have multi-month practical latency, not the day-or-two
originally assumed.

## 2026-09-18 - weather: train on history, predict with forecast, retrain on actuals

Plan for weather data in a live system: train models using historical
*actual* weather (as now, from Open-Meteo's archive). For a live
next-day prediction, feed in the weather *forecast* for that day (a
best guess, with its own error the model has never seen during
training). Once the day passes, the actual weather for it becomes
available - fold that into the next round of retraining so the
training data always reflects reality, not forecasts.
