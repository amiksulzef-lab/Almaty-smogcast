"""Weather-only model for the CHP-2 question.

No PM2.5 lags here on purpose: the model should only know the weather and the calendar.
Trained on the coal period, it says "with this weather, coal-era Almaty would have X".
After the switch to gas: if real PM2.5 is clearly below X, it's not just a warm winter.
"""
import lightgbm as lgb
import pandas as pd

from config import CHP2_SWITCH_DATE
from features import add_calendar, make_daily

WEATHER = ["temp", "temp_min", "humidity", "wind", "pressure", "precipitation",
           "blh", "blh_min", "blh_night", "wind_night"]

PARAMS = {
    "objective": "regression_l1",
    "learning_rate": 0.03,
    "num_leaves": 15,
    "min_child_samples": 20,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 1,
    "verbose": -1,
}
N_TREES = 400


def make_weather_table(hourly):
    daily = make_daily(hourly)
    daily = add_calendar(daily)
    # inversions build up over several days, so yesterday's weather too
    for col in ["temp", "blh", "blh_night", "wind"]:
        daily[col + "_yesterday"] = daily[col].shift(1)
    daily["temp_3d"] = daily.temp.rolling(3).mean()
    return daily


def weather_columns(use_blh=True):
    cols = WEATHER + ["temp_yesterday", "blh_yesterday", "blh_night_yesterday",
                      "wind_yesterday", "temp_3d",
                      "dayofweek", "weekend", "holiday", "heating", "dayofyear"]
    # Open-Meteo has no boundary layer height for Jan-Jun 2024 (checked all models).
    # so for winter 2023-24 the model with BLH is half blind. use_blh=False to compare
    if not use_blh:
        cols = [c for c in cols if not c.startswith("blh")]
    return cols


def winter_of(dates):
    # Dec 2024 and Jan-Feb 2025 belong to the "2024-25" winter
    year = dates.dt.year - (dates.dt.month < 7).astype(int)
    return year.astype(str) + "-" + (year + 1).astype(str).str[-2:]


def train_model(data, use_blh=True):
    cols = weather_columns(use_blh)
    data = data.dropna(subset=["pm25"])
    return lgb.train(PARAMS, lgb.Dataset(data[cols], data.pm25), num_boost_round=N_TREES)


def coal_period(daily):
    return daily[daily.date < CHP2_SWITCH_DATE]


def leave_one_winter_out(daily, use_blh=True):
    """For each past winter: train on all other coal-era data, predict that winter.

    This shows how wrong the model normally is for a whole winter. If after the switch
    the gap is bigger than this, it's probably a real effect and not noise.
    """
    coal = coal_period(daily).dropna(subset=["pm25"]).copy()
    coal["winter"] = winter_of(coal.date)
    heating = coal[coal.heating == 1]

    rows, preds = [], []
    for w in sorted(heating.winter.unique()):
        test = heating[heating.winter == w]
        if len(test) < 60:  # skip winters with very little data
            continue
        model = train_model(coal[coal.winter != w], use_blh)
        test = test.assign(expected=model.predict(test[weather_columns(use_blh)]))
        preds.append(test)
        rows.append({
            "winter": w,
            "days": len(test),
            "actual_mean": test.pm25.mean(),
            "expected_mean": test.expected.mean(),
            "gap_percent": (test.pm25.mean() / test.expected.mean() - 1) * 100,
        })
    return pd.DataFrame(rows).round(1), pd.concat(preds)
