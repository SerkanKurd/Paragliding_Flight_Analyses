import pandas as pd
from geopy.distance import geodesic
import math
from itertools import combinations
import prepare_flightlog as fl
import os


def distances_calc(points):
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371.0  # Earth's radius in kilometers
        # Convert degrees to radians
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        # Haversine formula
        a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * \
            math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    distances = {}
    for i in range(len(points)):
        for j in range(i+1, len(points)):
            distances[(points[i], points[j])] = haversine(
                *points[i], *points[j])
    return distances


def fai_olc_distance(points):
    distances = distances_calc(points)
    max_triangle_distance = 0
    best_triangle_points = None
    num_points = len(points)
    combinations_list = list(combinations(range(num_points), 3))
    for i, j, k in combinations_list:
        d1 = distances[(points[i], points[j])]
        d2 = distances[(points[j], points[k])]
        d3 = distances[(points[i], points[k])]
        total_distance = d1 + d2 + d3
        shortest_leg = min(d1, d2, d3)

        if shortest_leg >= 0.28 * total_distance:
            if total_distance > max_triangle_distance:
                max_triangle_distance = total_distance
                best_triangle_points = (points[i], points[j], points[k])

    best_distance = max(distances.values())

    return (max_triangle_distance,
            best_triangle_points,
            best_distance)


def calculate_distance(row):
    if row["previus_coordinate"] is None:
        return 0
    return geodesic(row["coordinate"], row["previus_coordinate"]).meters


def main(df: pd.DataFrame):
    def caluculate_total_distance(row):
        global prev_total_distance
        prev_total_distance += row["distance_m"]
        return prev_total_distance

    global prev_total_distance
    prev_total_distance = 0

    df = df.iloc[::10, :]

    start_coordinates = (df["latitude"].iloc[0], df["longitude"].iloc[0])
    df["total_distance_m"] = df.apply(
        lambda row: caluculate_total_distance(row), axis=1)
    df["total_distance_m2"] = df["distance_m"].sum()

    df["distance_from_start_m"] = df.apply(lambda row: geodesic(
        start_coordinates, (row["latitude"], row["longitude"])).meters, axis=1)
    df.head()

    # plt.figure(figsize=(10, 5))
    # plt.plot(df['time'], df['gps_altitude_m'])
    # plt.xlabel('Time')
    # plt.ylabel('Altitude (m)')
    # plt.title('Flight Altitude over Time')
    # plt.grid(True)
    # plt.show()

    flight_loginterval = df["elapsed_time"].iloc[1] - \
        df["elapsed_time"].iloc[0]
    time_difference = str(pd.to_datetime(
        df['datetime'].iloc[-1]) - pd.to_datetime(df['datetime'].iloc[0]))

    coordinates = list(zip(df["latitude"].tolist(), df["longitude"].tolist()))
    triangle_distance, best_triangle_points, best_distance = fai_olc_distance(
        coordinates)
    sonuc = {
        "Toplam mesafe": f"{df['total_distance_m'].iloc[-1] / 1000:.1f} km",
        "Maksimum yükseklik": f"{df['gps_altitude_m'].max():.0f} m",
        "Maksimum tırmanma hızı": f"{df['climb_rate_m/s'].max():.2f} m/s",
        "Maksimum iniş hızı": f"{df['climb_rate_m/s'].min():.2f} m/s",
        "Maksimum uzaklık": f"{df['distance_from_start_m'].max() / 1000:.1f} km",
        "Ortalama hız": f"{df['speed_km_h'].mean():.1f} km/h",
        "Maksimum hız": f"{df['speed_km_h'].max():.1f} km/h",
        "Toplam süre": str(time_difference),
        "Maksimum irtifa": f"{df['pressure_altitude_m'].max():.0f} m",
        "Minimum irtifa": f"{df['pressure_altitude_m'].min():.0f} m",
        "Kalkış irtifası": f"{df['pressure_altitude_m'].iloc[0]:.0f} m",
        "Kayıt aralığı (log interval)": f"{flight_loginterval} sn",
        "Maximum FAI OLC Triangle Distance": f"{triangle_distance:.2f} km.",
        "Best Distance": f"{best_distance:.2f} km.",
        "Best Triangle Points": best_triangle_points
    }
    return sonuc


if __name__ == "__main__":
    filedir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(
        filedir, "data", "flightlogs", "2025-05-10-XCT-FBA-02.igc")
    if not os.path.exists(file_path):
        print(f"File not found at {file_path}. Please check the path.")
    else:
        print(main(fl.prepare_data(file_path)))
