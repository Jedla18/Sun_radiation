from typing import List
import requests

## vstupy ##
#latitude : float = 49.83754
#longitude : float = 18.15603
gps : str = "48° 51' 30\" N, 2° 17' 40\" E"
start_date : str = "2024-06-01"
end_date : str = "2024-06-02"
tilt : int = 30 #°
azimuth : int = -45 #°
area : int = 10 #m²

####
def get_latitude_and_longitude(gps :str) -> (float, float):

    parts = gps.split(',')

    def get_number_from_gps(one_side : str) -> float:

        main_number : int = 0; minutes : int = 0; seconds : int = 0; sumary : float = 0
        index_before : int = 0

        for i in range(len(one_side)):

            if one_side[i] == "°":
                main_number = int(one_side[index_before:i])
                index_before = i+1

            if one_side[i] == "'":
                minutes = int(one_side[index_before:i])
                index_before = i+1

            if one_side[i] == '"':
                seconds = int(one_side[index_before:i])
                index_before = i+1

            if one_side[i] in "NSEW":
                sumary = main_number + minutes / 60 + seconds /3600
                break

        if one_side[-1] in "SW":
             sumary *= -1

        return sumary

    latitude: float = get_number_from_gps(parts[0])
    longitude: float = get_number_from_gps(parts[1])

    return latitude, longitude


def get_data_from_parameter(frequency : str, parameter : str) -> dict:
    # Nastavení parametrů
    url = "https://archive-api.open-meteo.com/v1/archive"

    latitude, longitude = get_latitude_and_longitude(gps)


    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        frequency : parameter,
        "tilt": tilt,            # sklon
        "azimuth": azimuth         # uhel
    }

    # Odeslání požadavku
    response = requests.get(url, params=params)

    assert response.status_code == 200

    data : dict = response.json()

    return data

def get_radiation_from_data() -> List[float]:

    data_hourly : dict = get_data_from_parameter("hourly",'global_tilted_irradiance')
    #data_time_hourly : List[str] = data_hourly["hourly"]["time"]
    data_total_radiation_hourly : List[float] = data_hourly["hourly"]['global_tilted_irradiance']

    return data_total_radiation_hourly


def calculate_radiation_to_days() -> List[float]:

    data_total_radiation_hourly : List[float] = get_radiation_from_data()

    data_total_radiation_hourly_by_day : List[float] = []

    for i in range(0, len(data_total_radiation_hourly), 24):
        soucet : float = sum(data_total_radiation_hourly[i:i+24])
        data_total_radiation_hourly_by_day.append(soucet)

    return data_total_radiation_hourly_by_day


def calculate_radiation_to_square(square_metears : int) -> List[float]:

    data_total_radiation_hourly_by_day : List[float] = calculate_radiation_to_days()

    for i in range(len(data_total_radiation_hourly_by_day)):
        data_total_radiation_hourly_by_day[i] *= square_metears

    return data_total_radiation_hourly_by_day


def calculate_total_radiation(data_radiation : List[float]) -> float:
    return sum(data_radiation)

print("slunecni radiace jednotlive dny[W]: ")
print(calculate_radiation_to_square(area))
print("\n")
print("slunecni radiace celkem[W]: ")
print(calculate_total_radiation(calculate_radiation_to_square(area)))

lat, long = get_latitude_and_longitude("48° 51' 30\" N, 2° 17' 40\" E")

print(lat, long)
