import pandas as pd
import os


def parse_trackpoint(line):
    # Extract components from the line
    time_utc = line[1:7]  # HHMMSS
    latitude_raw = line[7:15]  # DDMMmmmN
    longitude_raw = line[15:24]  # DDDMMmmmE
    gps_altitude = int(line[25:30])  # GGGG
    pressure_altitude = int(line[30:35])  # LLLL

    # Convert UTC time
    hours = int(time_utc[:2])
    minutes = int(time_utc[2:4])
    seconds = int(time_utc[4:6])

    # Convert latitude to decimal degrees
    latitude_deg = int(latitude_raw[:2])
    latitude_min = float(latitude_raw[2:7]) / 1000
    latitude = latitude_deg + latitude_min / 60
    if latitude_raw[7] == 'S':
        latitude *= -1

    # Convert longitude to decimal degrees
    longitude_deg = int(longitude_raw[:3])
    longitude_min = float(longitude_raw[3:8]) / 1000
    longitude = longitude_deg + longitude_min / 60
    if longitude_raw[8] == 'W':
        longitude *= -1

    return {
        "time": f"{hours:02}:{minutes:02}:{seconds:02}",
        "latitude": latitude,
        "longitude": longitude,
        "gps_altitude_m": gps_altitude,
        "pressure_altitude_m": pressure_altitude,
    }


def getfile(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()

    flight_data = [line for line in lines if line.startswith('B')]
    flight_date = [line for line in lines if line.startswith(
        'HFDTE')][0][-7:].strip()
    pilot_name = [line for line in lines if "PILOT" in line][0]
    pilot_name = pilot_name.split(":")[1].strip()
    df = pd.DataFrame([parse_trackpoint(line) for line in flight_data])
    df.insert(
        0,
        "date",
        pd.to_datetime(
            flight_date,
            format='%d%m%y',
            dayfirst=True,
            errors='coerce')
    )
    df.insert(1, "pilot", pilot_name)
    df.insert(0, "filename", file_name.split("\\")[-1])
    df = df.iloc[::10, :]

    if os.path.exists(os.path.join("data", "flight_data.csv")):
        df.to_csv(os.path.join("data", "flight_data.csv"),
                  mode="a", header=False, index=False)
    else:
        df.to_csv(os.path.join("data", "flight_data.csv"),
                  header=True, index=False)


def main():
    if os.path.exists(os.path.join("data", "flight_data.csv")):
        os.remove(os.path.join("data", "flight_data.csv"))
    files = os.listdir("flightlogs")
    for file in files:
        if file.endswith(".igc"):
            print(file, "-->start")
            getfile(os.path.join("flightlogs", file))
            print(file, "-->done")
    print(len(files), "file(s) processed successfully.")


if __name__ == "__main__":
    main()
