import pandas as pd
import weather_data as getweatherdata
from IGC_file_parse import getfile as igc
from functools import lru_cache
from geopy.distance import geodesic
import math
import os
import db_connection as db


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
    df = igc(filename)

    df["previous_latitude"] = df["latitude"].shift(1)
    df["previous_longitude"] = df["longitude"].shift(1)
    df.fillna(0, inplace=True)
    # df.drop(df.index[0], inplace=True)

    df["distance_from_takeoff_m"] = df.apply(
        lambda row: geodesic(
            (row["latitude"], row["longitude"]),
            (df["latitude"].iloc[0], df["longitude"].iloc[0])).meters, axis=1)

    df["distance_m"] = df.apply(lambda row: geodesic(
        (row["previous_latitude"], row["previous_longitude"]),
        (row["latitude"], row["longitude"])).meters, axis=1)

    df["speed_km/s"] = ((df["distance_m"]/1000) /
                        (df["datetime"].diff().dt.total_seconds()/3600))

    df["climb_m"] = df["pressure_altitude_m"].diff()
    df["climb_m(delta)"] = df["pressure_altitude_m"].diff(20)
    df["climb_rate_m/s"] = df["climb_m"] / \
        df["datetime"].diff().dt.total_seconds()
    df["glide_ratio"] = df.apply(
        lambda row: row["distance_m"] /
        abs(row["climb_m"]) if row["climb_m"] != 0 else 0,
        axis=1)

    df["bearing"] = df.apply(calculate_bearing, axis=1)
    df["delta_bearing"] = abs((df["bearing"].diff() + 180) % 360 - 180)

    df["elapsed_time"] = (
        df["datetime"] - df["datetime"].iloc[0]).dt.total_seconds()
    df["delta_time"] = (df["datetime"].diff()).dt.total_seconds()

    df[["temp",
        "pressure",
        "humidity",
        "dew_point",
        "wind_speed",
        "wind_deg"]] = df.apply(get_weather_data,
                                axis=1,
                                result_type="expand")

    # find and delete before take off
    mask = df["speed_km/s"] > 25
    true_idx = mask[mask].index

    if len(true_idx):
        first_true = true_idx[0]
        last_true = true_idx[-1]
    else:
        first_true = last_true = None
    df = df.loc[first_true:last_true].reset_index(drop=True)

    return df


def main():
    db.delete_db("flights")
    file_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(file_dir)
    flightlogs_dir = os.path.join(base_dir, "data", "raw")
    files = [f for f in os.listdir(flightlogs_dir)
             if f.endswith(".igc") or f.endswith(".IGC")]
    # files = files[:3]  # Limit to first file for testing
    df = pd.DataFrame()
    error_files = []
    db.delete_db("flights")
    for file in files:
        file_path = os.path.join(flightlogs_dir, file)
        print("\n", "------------------------------------------------------")
        print(f"Processing {files.index(file)+1}/{len(files)} File: {file}\n")
        print(f"Processing {file_path}...\n")
        try:
            df_prepare = prepare_data(file_path)
            print(df_prepare.head())
            df = pd.concat([df_prepare, df], ignore_index=True)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            error_files.append(file)
            continue
    if df.empty:
        print("No data to save.")
        return
    print("Saving data to database...")
    for error_file in error_files:
        print(f"\n{error_file.index} Error processing file: {error_file}")
    db.write_db(df, "flights")


if __name__ == "__main__":
    main()
