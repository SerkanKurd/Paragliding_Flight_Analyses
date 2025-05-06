import requests
import pandas as pd
from datetime import datetime, timezone
import db_connection as db


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

    matched_rows = db.getdata("weather_data", f"lat = {lat} AND lon = {lon} AND dt = {dt}")

    if matched_rows == []:
        weather_json = api_call(lat, lon, dt)
        weather_data = pd.json_normalize(weather_json["data"][0])
        weather_data["lat"] = lat
        weather_data["lon"] = lon
        weather_data["datetime"] = timestamp
        weather_data = weather_data[["lat", "lon", "datetime", "dt", "temp",
                                     "pressure", "humidity", "dew_point",
                                     "wind_speed", "wind_deg"]]
        matched_rows = weather_data.values.tolist()

        db.write_db(weather_data, "weather_data")

    return matched_rows[4:]


if __name__ == "__main__":
    # testing
    print(main(36.539000, 29.169517, "2025-04-05 12:35:00"))
