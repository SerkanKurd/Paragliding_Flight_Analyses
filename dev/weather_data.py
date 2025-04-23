import requests
import pandas as pd
from datetime import datetime, timezone
import os


def api_call(lat, lon, dt):
    # OpenWeatherMap API call
    url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&units=metric&dt={dt}&appid=bedfa32222f31e3d52efbe3fc142575e"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return f"Request failed with status {response.status_code}"


def main(lat, lon, timestamp):

    lat = round(lat, 1)
    lon = round(lon, 1)
    if type(timestamp) is str:
        timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

    timestamp = timestamp.replace(tzinfo=timezone.utc,
                                  minute=0, second=0, microsecond=0)
    dt = int(timestamp.timestamp())

    if os.path.exists(os.path.join("data", "weather_data.csv")):
        df = pd.read_csv(os.path.join("data", "weather_data.csv"))
        matched_rows = df[(df["lat"] == lat) &
                          (df["lon"] == lon) &
                          (df["dt"] == dt)]
    else:
        matched_rows = pd.DataFrame()

    if matched_rows.empty:
        weather_json = api_call(lat, lon, dt)
        weather_data = pd.json_normalize(weather_json["data"][0])
        weather_data["lat"] = lat
        weather_data["lon"] = lon
        weather_data["datetime"] = timestamp
        weather_data = weather_data[["lat", "lon", "datetime", "dt", "temp",
                                     "pressure", "humidity", "dew_point",
                                     "wind_speed", "wind_deg"]]

        if "df" in locals():
            df = pd.concat([df, weather_data], ignore_index=True)
        else:
            df = weather_data

        df.to_csv(os.path.join("data", "weather_data.csv"), index=False)

        result = pd.Series(weather_data[[
                           "temp", "pressure", "humidity",
                           "dew_point", "wind_speed", "wind_deg"]].iloc[0])
    else:
        result = pd.Series(matched_rows[[
                           "temp", "pressure", "humidity",
                           "dew_point", "wind_speed", "wind_deg"]].iloc[0])

    return result.values.tolist()


if __name__ == "__main__":
    # testing
    print(main(36.539000, 29.169517, "2025-04-05 12:35:00"))
