import pandas as pd
from geopy.distance import geodesic
import math
import getweatherdata
import os
from IGC_file_parse import getfile as igc
import folium as fm


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


def get_weather_data(row):
    lat = float(row["latitude"])
    lon = float(row["longitude"])
    timestamp = row["datetime"]
    result = getweatherdata.main(lat, lon, timestamp)
    return result


def create_map(df):
    coordinates = df[["latitude", "longitude"]].values.tolist()
    zone = df["zone"].values.tolist()
    climb_rate = df["climb_rate_m/s"].values.tolist()
    elapsed_time = df["elapsed_time"].values.tolist()

    map = fm.Map(location=coordinates[0], zoom_start=13)
    for x in range(len(coordinates)):
        if zone[x] == "thermal":
            color_ = 'red'
        else:
            color_ = 'blue'
        fm.CircleMarker(
            location=coordinates[x],
            radius=1,
            color=color_,
            fill=True,
            fill_color=color_,
            popup=(f"{elapsed_time[x]}, \n{climb_rate[x]}")).add_to(map)
    fm.Marker(location=coordinates[0], popup="Takeoff").add_to(map)
    fm.Marker(location=coordinates[-1], popup="Landing").add_to(map)
    map.save("map.html")


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
    # find and delete before take off
    for index, row in df.iterrows():
        if row["speed_km/s"] > 10:
            df = df.iloc[index:]
            df.reset_index(drop=True, inplace=True)
            break
    df["elapsed_time"] = (
        df["datetime"] - df["datetime"].iloc[0]).dt.total_seconds()

    df["zone"] = df.apply(lambda row: "thermal" if (
        row["climb_m(delta)"] > 0 or
        row["climb_rate_m/s"] > 0)
        else "standart", axis=1)
    df[["temp", "pressure", "humidity", "dew_point", "wind_speed", "wind_deg"]
       ] = df.apply(get_weather_data, axis=1, result_type="expand")

    df.drop(["filename", "pilot", "previous_latitude", "previous_longitude",
            "climb_m", "distance_m"], axis=1, inplace=True)
    df = df[df["zone"] == "thermal"]
    df = df[["datetime",
             "latitude",
             "longitude",
             "gps_altitude_m",
             "pressure_altitude_m",
             "distance_from_takeoff_m",
             "speed_km/s",
             "climb_rate_m/s",
             "bearing",
             "glide_ratio",
             "elapsed_time"]]
    df.head()
    return df


if __name__ == "__main__":
    df = pd.DataFrame()
    files = os.listdir("flightlogs")
    for file in files:
        df_prepare = prepare_data(file)
        df = pd.concat([df_prepare, df], ignore_index=True)
        print(df.info())
    # df.to_csv(os.path.join("data", "flight_data_processed.csv"), index=False)

    # create_map(df[["latitude",
    #                "longitude",
    #                "zone",
    #                "climb_rate_m/s",
    #                "elapsed_time"]])
