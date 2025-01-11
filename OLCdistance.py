import math
from itertools import combinations


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
            best_distance,
            distances)


if __name__ == "__main__":
    pass
