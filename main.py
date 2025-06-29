
import requests

## vstupy ##
latitude = 50.1
longitude = 14.4
start_date = "2024-06-01"
end_date = "2024-06-02"
tilt = 30 #	°
azimuth = -45 #	°
area = 10 #m²

####

def get_data_from_parameters(frequency, parameters):
    # Nastavení parametrů
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        frequency : parameters,
        "tilt": tilt,            # sklon
        "azimuth": azimuth         # uhel
    }

    # Odeslání požadavku
    response = requests.get(url, params=params)

    assert response.status_code == 200

    data = response.json()

    return data


def get_radiation_from_data():

    data_hourly = get_data_from_parameters("hourly",'global_tilted_irradiance')
    data_time_hourly = data_hourly["hourly"]["time"]
    data_total_radiation_hourly = data_hourly["hourly"]['global_tilted_irradiance']

    return data_total_radiation_hourly


def calculate_radiation_to_days():

    data_total_radiation_hourly = get_radiation_from_data()

    data_total_radiation_hourly_by_day = []

    for i in range(0, len(data_total_radiation_hourly), 24):
        soucet = sum(data_total_radiation_hourly[i:i+24])
        data_total_radiation_hourly_by_day.append(soucet)

    return data_total_radiation_hourly_by_day


def calculate_radiation_to_square(square_metears):

    data_total_radiation_hourly_by_day = calculate_radiation_to_days()

    for i in range(len(data_total_radiation_hourly_by_day)):
        data_total_radiation_hourly_by_day[i] *= square_metears

    return data_total_radiation_hourly_by_day


def calculate_total_radiation(data_radiation) : return sum(data_radiation)

print("slunecni radiace jednotlive dny[W]: ")
print(calculate_radiation_to_square(area))
print("\n")
print("slunecni radiace celkem[W]: ")
print(calculate_total_radiation(calculate_radiation_to_square(area)))
