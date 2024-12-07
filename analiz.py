import pandas as pd
import matplotlib.pyplot as plt

# Dosyayı okuyalım
file_path =   "E:/Wolf/Belgeler/Projelerim/Python Projeleri/Uçuş Analiz/2024-05-19 10_05_00.igc"

with open(file_path, 'r') as file:
    lines = file.readlines()

# IGC dosyasındaki B-record (uçuş kayıtları) satırlarını filtreleyelim
flight_data = [line for line in lines if line.startswith('B')]

# Her B-record satırını çözümleyelim ve bir DataFrame oluşturalım
records = []
for record in flight_data:
    time = record[1:7]
    latitude = record[7:15]
    longitude = record[15:24]
    altitude = record[25:30]
    records.append([time, latitude, longitude, altitude])

# DataFrame'e dönüştürelim
df = pd.DataFrame(records, columns=['Time', 'Latitude', 'Longitude', 'Altitude'])

# Zaman ve irtifa verilerini dönüştürelim
#df['Time'] = pd.to_datetime(df['Time'], format='%H%M%S').dt.time
#df['Altitude'] = pd.to_numeric(df['Altitude'], errors='coerce')

# NaN değerlerini kaldıralım
df = df.dropna(subset=['Altitude'])

# Zaman ve irtifa verilerini plot edelim
plt.figure(figsize=(10, 5))
plt.plot(df['Time'], df['Altitude'])
plt.xlabel('Time')
plt.ylabel('Altitude (m)')
plt.title('Flight Altitude over Time')
plt.grid(True)
plt.show()
