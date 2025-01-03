import math


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points
    on the Earth using the Haversine formula.

    Parameters:
    lat1, lon1 : Latitude and longitude of point 1 (in decimal degrees)
    lat2, lon2 : Latitude and longitude of point 2 (in decimal degrees)

    Returns:
    Distance in kilometers.
    """
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


def fai_olc_distance(points):
    """
    Calculate the FAİ OLC distance for a given set of GPS points.

    Parameters:
    points : List of tuples [(lat, lon), ...]
             List of latitude and longitude coordinates in decimal degrees.

    Returns:
    The maximum FAI OLC distance and the triangle points.
    """
    n = len(points)
    max_distance = 0
    best_triangle = None

    # Iterate through all possible triangles
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                # Calculate distances between points
                d1 = haversine(*points[i], *points[j])
                d2 = haversine(*points[j], *points[k])
                d3 = haversine(*points[k], *points[i])
                print(d1, d2, d3)
                # Check if it forms a valid FAI triangle
                total_distance = d1 + d2 + d3
                shortest_leg = min(d1, d2, d3)

                if shortest_leg >= 0.28 * total_distance:
                    if total_distance > max_distance:
                        max_distance = total_distance
                        best_triangle = (points[i], points[j], points[k])

    return max_distance, best_triangle


# Example usage
if __name__ == "__main__":
    # List of GPS points (latitude, longitude)
    gps_points = [(40.0312, 32.3283), (40.01063333333333, 32.29765)]
    distance, triangle = fai_olc_distance(gps_points)
    print(f"Maximum FAI OLC Distance: {distance:.2f} km")
    print(f"Triangle Points: {triangle}")
