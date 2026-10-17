"""Weekly CHP-2 check. Run this every week during winter 2026-27:

    python src/download_weather.py
    python src/download_openaq.py
    python src/build_dataset.py
    python src/chp2_tracker.py

It trains the weather-only model on the coal period and compares its "expected" PM2.5
with what really happened after CHP2_SWITCH_DATE (see config.py).
"""
import matplotlib.pyplot as plt

from config import CHP2_SWITCH_DATE, FIGURES_DIR, RESULTS_DIR
from features import load_hourly
from weather_model import coal_period, leave_one_winter_out, make_weather_table, train_model, weather_columns


def main():
    daily = make_weather_table(load_hourly())
    after = daily[daily.date >= CHP2_SWITCH_DATE].dropna(subset=["pm25"])
    print(f"switch date in config: {CHP2_SWITCH_DATE}")

    # how big is the normal error for a whole winter
    past, _ = leave_one_winter_out(daily)
    print("\npast winters, model trained without that winter:")
    print(past.to_string(index=False))
    normal_range = past.gap_percent.abs().max() if len(past) else float("nan")

    if len(after) == 0:
        print("\nno data after the switch date yet, nothing to compare")
        return

    model = train_model(coal_period(daily))
    after = after.assign(expected=model.predict(after[weather_columns()]))

    gap = (after.pm25.mean() / after.expected.mean() - 1) * 100
    print(f"\nafter switch: {len(after)} days")
    print(f"real mean PM2.5:     {after.pm25.mean():.1f}")
    print(f"expected (coal era): {after.expected.mean():.1f}")
    print(f"difference: {gap:+.1f}%")
    print(f"past winters were off by up to {normal_range:.1f}%")
    if abs(gap) <= normal_range:
        print("-> still inside normal model error, can't say anything yet")
    else:
        print("-> bigger than the usual error, could be a real effect (or something else changed)")

    weekly = after.set_index("date")[["pm25", "expected"]].resample("W").mean()
    print("\nby week:")
    print(weekly.round(1).to_string())
    weekly.round(1).to_csv(RESULTS_DIR / "chp2_weekly.csv")

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(after.date, after.pm25, label="real PM2.5", color="black")
    ax.plot(after.date, after.expected, label="expected with coal-era behaviour", color="tab:red", alpha=0.8)
    ax.set_ylabel("PM2.5, µg/m³ (daily mean)")
    ax.set_title(f"After CHP-2 switch ({CHP2_SWITCH_DATE}): real vs weather-expected")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "chp2_tracker.png", dpi=120)
    print(f"\nsaved {FIGURES_DIR / 'chp2_tracker.png'}")


if __name__ == "__main__":
    main()
