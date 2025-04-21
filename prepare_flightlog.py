import pandas as pd
import weather_data as getweatherdata
from IGC_file_parse import getfile as igc
from functools import lru_cache
from geopy.distance import geodesic
import math
import os


def calculate_bearing(row):
    lat1 = math.radians(row["previous_latitude"])
    lon1 = math.radians(row["previous_longitude"])
    lat2 = math.radians(row["latitude"])
    lon2 = math.radians(row["longitude"])

    delta_lon = lon2 - lon1

    x = math.sin(delta_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
                                           * math.cos(lat2) *
                                           math.cos(delta_lon))

    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = int((initial_bearing + 360) % 360)

    return compass_bearing


def calculate_distance(row):
    return geodesic((row["previous_latitude"], row["previous_longitude"]),
                    (row["latitude"], row["longitude"])).meters


@lru_cache(maxsize=10000)
def get_weather_data_cached(lat, lon, timestamp):
    return getweatherdata.main(lat, lon, timestamp)


def get_weather_data(row):
    lat = float(row["latitude"])
    lon = float(row["longitude"])
    timestamp = str(row["datetime"])
    return get_weather_data_cached(lat, lon, timestamp)


def prepare_data(filename):
    df = igc(os.path.join("flightlogs", filename), 1)
    df["previous_latitude"] = df["latitude"].shift(1)
    df["previous_longitude"] = df["longitude"].shift(1)
    df["distance_from_takeoff_m"] = df.apply(
        lambda row: geodesic(
            (row["latitude"], row["longitude"]),
            (df["latitude"].iloc[0], df["longitude"].iloc[0])).meters, axis=1)
    df.drop(df.index[0], inplace=True)
    df["distance_m"] = df.apply(lambda row: geodesic(
        (row["previous_latitude"], row["previous_longitude"]),
        (row["latitude"], row["longitude"])).meters, axis=1)
    df["speed_km/s"] = ((df["distance_m"]/1000) /
                        (df["datetime"].diff().dt.total_seconds()/3600))
    df["climb_m"] = df["gps_altitude_m"].diff()
    df["climb_m(delta)"] = df["gps_altitude_m"].diff(20)
    df["climb_rate_m/s"] = df["climb_m"] / \
        df["datetime"].diff().dt.total_seconds()
    df["bearing"] = df.apply(calculate_bearing, axis=1)
    df["delta_bearing"] = abs((df["bearing"].diff() + 180) % 360 - 180)
    df["glide_ratio"] = df.apply(
        lambda row: row["distance_m"] /
        abs(row["climb_m"]) if row["climb_m"] != 0 else 0,
        axis=1)
    df.fillna(0, inplace=True)
    df["elapsed_time"] = (
        df["datetime"] - df["datetime"].iloc[0]).dt.total_seconds()
    df["zone"] = df.apply(lambda row: "thermal" if (
        row["climb_m(delta)"] > 0 or
        row["climb_rate_m/s"] > 0)
        else "standart", axis=1)
    df[["temp",
        "pressure",
        "humidity",
        "dew_point",
        "wind_speed",
        "wind_deg"]] = df.apply(get_weather_data, axis=1, result_type="expand")

    # find and delete before take off
    mask = df["speed_km/s"] > 10
    if mask.any():
        first_idx = mask.idxmax()
        df = df.loc[first_idx:].reset_index(drop=True)
    else:
        df = df.iloc[0:0]
    return df


if __name__ == "__main__":
    if os.path.exists(os.path.join("data", "flight_data.csv")):
        df = pd.read_csv(os.path.join(
            "data", "flight_data.csv"), low_memory=False)
        df_files = set(df["filename"].tolist())
    else:
        df = pd.DataFrame()
        df_files = set()

    if not os.path.exists("flightlogs"):
        print("flightlogs folder not exist")
        exit()

    files = [f for f in os.listdir("flightlogs") if f.lower().endswith(".igc")]
    for file in files:
        if file in df_files:
            print("This file already in data frame skipped:", file)

    files = [f for f in files if f not in df_files]
    for file in files:
        print(f"Processing {files.index(file)+1}/{len(files)} File: {file}")
        try:
            df_prepare = prepare_data(file)
        except Exception as e:
            print("Error on", file, ":", e)
            continue
        print(df_prepare.head())
        df_prepare["filename"] = file
        df = pd.concat([df_prepare, df], ignore_index=True)
        df.to_csv(os.path.join("data", "flight_data.csv"),
                  index=False)

    print(f"Processed {len(df)} rows")
    print("Data saved to flight_data.csv")
