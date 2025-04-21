import pandas as pd
import weather_data as getweatherdata
from IGC_file_parse import getfile as igc
import os
from functools import lru_cache


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
    df.fillna(0, inplace=True)
    df[["temp",
        "pressure",
        "humidity",
        "dew_point",
        "wind_speed",
        "wind_deg"]] = df.apply(get_weather_data, axis=1, result_type="expand")
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
