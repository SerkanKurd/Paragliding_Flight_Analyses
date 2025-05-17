import requests
import pandas as pd
from datetime import datetime, timezone
import app.utils.db_connection as db
import os
import json


def get_api_key():
    file_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(file_dir)
    file_path = os.path.join(base_dir, "data", "weather_api_key.json")
    with open(file_path, "r") as f:
        api_key = json.load(f)
    return api_key["api_key"]


def api_call(lat, lon, dt):
    # OpenWeatherMap API call
    url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&units=metric&dt={dt}&appid={get_api_key()}"
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

    matched_rows = db.getdata(
        "weather_data", f"lat = {lat} AND lon = {lon} AND dt = {dt}")

    if matched_rows == []:
        weather_json = api_call(lat, lon, dt)
        weather_data = pd.json_normalize(weather_json["data"][0])
        weather_data["lat"] = lat
        weather_data["lon"] = lon
        weather_data["datetime"] = timestamp
        weather_data = weather_data[["lat", "lon", "datetime", "dt", "temp",
                                     "pressure", "humidity", "dew_point",
                                     "wind_speed", "wind_deg"]]
        matched_rows = weather_data.values.tolist()[0]

        db.write_db(weather_data, "weather_data", "append")

    return matched_rows[4:]


if __name__ == "__main__":
    # testing
    print(main(36.539000, 29.169517, "2025-05-10 12:35:00"))
