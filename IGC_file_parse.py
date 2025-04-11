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


def getfile(file_name, loginterval=1):
    with open(file_name, 'r') as file:
        lines = file.readlines()

    flight_data = [line for line in lines if line.startswith('B')]
    flight_date = [line for line in lines if line.startswith(
        'HFDTE')][0].strip()
    for x in range(len(flight_date)):
        if flight_date[x].isdigit():
            flight_date = flight_date[x:x + 6]
            break
    pilot_name = [line for line in lines if "PILOT" in line][0]
    pilot_name = pilot_name.split(":")[1].strip()
    df = pd.DataFrame([parse_trackpoint(line) for line in flight_data])
    df["datetime"] = pd.to_datetime(
        flight_date + " " + df["time"], format="%d%m%y %H:%M:%S")
    df["pilot"] = pilot_name
    df["filename"] = file_name.split("\\")[-1]
    df = df[[
        "filename",
        "datetime",
        "pilot",
        "latitude",
        "longitude",
        "gps_altitude_m",
        "pressure_altitude_m"
    ]]

    if loginterval > 1:
        # Downsample the DataFrame
        df = df.iloc[::loginterval, :]

    return df  # Pandas DataFrame with parsed data


def main():
    # Example usage
    file = os.listdir("flightlogs")[0]
    df = getfile("flightlogs\\" + file, 10)
    print(df.head())
    print(df.info())


if __name__ == "__main__":
    main()
