import folium as fm
import os


def create_map(df):
    coordinates = df[["latitude", "longitude"]].values.tolist()
    climb_rate = df["climb_rate_m/s"].values.tolist()
    elapsed_time = df["elapsed_time"].values.tolist()
    zone = df["zone"].values.tolist()
    zone = ["red" if x == "thermal" else "blue" for x in zone]
    map = fm.Map(location=coordinates[0], zoom_start=13)
    for x in range(len(coordinates)):
        fm.CircleMarker(
            location=coordinates[x],
            radius=1,
            color=zone[x],
            fill=True,
            fill_color=zone[x],
            popup=(f"{elapsed_time[x]}, \n{climb_rate[x]}")).add_to(map)
    fm.Marker(location=coordinates[0], popup="Takeoff").add_to(map)
    fm.Marker(location=coordinates[-1], popup="Landing").add_to(map)
    map.save(os.path.join("data", "map.html"))
