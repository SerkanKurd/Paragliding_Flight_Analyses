import math
import pandas as pd
from itertools import combinations


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth's radius in kilometers

    # Convert degrees to radians
    phi1, phi2 = math.radians(lat1),   math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * \
        math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def fai_olc_distance(points):
    max_distance = 0
    best_triangle = None
    num_points = len(points)
    combinations_list = list(combinations(range(num_points), 3))
    for i, j, k in combinations_list:
        d1 = haversine(*points[i], *points[j])
        d2 = haversine(*points[j], *points[k])
        d3 = haversine(*points[k], *points[i])
        total_distance = d1 + d2 + d3
        shortest_leg = min(d1, d2, d3)

        if shortest_leg >= 0.28 * total_distance:
            if total_distance > max_distance:
                max_distance = total_distance
                best_triangle = (points[i], points[j], points[k])

    return max_distance, best_triangle


if __name__ == "__main__":
    df = pd.read_csv("flight_data.csv")
    gps_points = list(zip(df['latitude'].values.tolist(),
                      df['longitude'].values.tolist()))
    distance, triangle = fai_olc_distance(gps_points)
    print(f"Maximum FAI OLC Distance: {distance:.2f} km")
    print(f"Triangle Points: {triangle}")
