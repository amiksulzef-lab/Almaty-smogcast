"""Download hourly historical weather for Almaty from the Open-Meteo archive (ERA5). No API key needed."""
from datetime import date, timedelta

import pandas as pd
import requests

from config import LATITUDE, LONGITUDE, RAW_DIR, START_DATE, TIMEZONE

URL = "https://archive-api.open-meteo.com/v1/archive"
VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
    "wind_direction_10m",
    "surface_pressure",
    "precipitation",
    "boundary_layer_height",  # low boundary layer = pollution gets trapped (inversions)
]


def main():
    # The archive lags a few days behind today
    end_date = (date.today() - timedelta(days=5)).isoformat()
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": START_DATE,
        "end_date": end_date,
        "hourly": ",".join(VARIABLES),
        "timezone": TIMEZONE,
    }
    response = requests.get(URL, params=params, timeout=120)
    response.raise_for_status()

    df = pd.DataFrame(response.json()["hourly"])
    df["time"] = pd.to_datetime(df["time"])

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out = RAW_DIR / "weather.csv"
    df.to_csv(out, index=False)
    print(f"Saved {len(df)} rows to {out}")


if __name__ == "__main__":
    main()
