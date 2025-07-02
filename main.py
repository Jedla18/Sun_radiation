from typing import List

import pvlib.irradiance
import requests
import pandas as pd
from pvlib.location import Location
from timezonefinder import TimezoneFinder

#https://open-meteo.com/en/docs/historical-weather-api?start_date=2023-07-14&hourly=global_tilted_irradiance,direct_normal_irradiance,diffuse_radiation,cloud_cover,terrestrial_radiation&latitude=50.06847&longitude=14.45161&end_date=2023-07-14
#https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.irradiance.get_total_irradiance.html#pvlib.irradiance.get_total_irradiance

## vstupy fixni zatim ##
gps : str = "48° 51' 30\" N, 2° 17' 40\" E"
start_date : str = "2024-06-01"
end_date : str = "2024-06-02"
####


def get_latitude_and_longitude() -> (float, float):

    parts = gps.split(',')

    def get_number_from_gps(one_side : str) -> float:

        main_number : int = 0; minutes : int = 0; seconds : int = 0
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


        sumary: float = main_number + minutes / 60 + seconds /3600

        if one_side[-1] in "SW" or one_side[0] in "SW":
             sumary *= -1

        return sumary

    latitude: float = get_number_from_gps(parts[0])
    longitude: float = get_number_from_gps(parts[1])

    return latitude, longitude


def get_data_from_parameter(tilt: int, azimuth: int) -> dict:
    # Nastavení parametrů
    url = "https://archive-api.open-meteo.com/v1/archive"

    latitude, longitude = get_latitude_and_longitude()


    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly" :{ "direct_normal_irradiance","global_tilted_irradiance","diffuse_radiation"},
        "tilt": tilt,            # sklon
        "azimuth": azimuth         # uhel
    }

    # Odeslání požadavku
    response = requests.get(url, params=params)

    assert response.status_code == 200

    data_from_api : dict = response.json()

    return data_from_api

def get_types_of_radiations_from_data(tilth : int,azimuth : int) -> dict:

    data_from_api_hourly : dict = get_data_from_parameter(tilth,azimuth)
    data_time_hourly : List[str] = data_from_api_hourly["hourly"]["time"]
    data_direct_normal_irradiance_hourly : List[float] = data_from_api_hourly["hourly"]['direct_normal_irradiance']
    data_global_tilted_irradiance_hourly : List[float] = data_from_api_hourly["hourly"]['global_tilted_irradiance']
    data_diffuse_radiation_hourly : List[float] = data_from_api_hourly["hourly"]['diffuse_radiation']

    sorted_data : dict = {
        "dni" : data_direct_normal_irradiance_hourly,
        "ghi" : data_global_tilted_irradiance_hourly,
        "dhi" : data_diffuse_radiation_hourly,
        "time": data_time_hourly
    }

    return sorted_data


def calculate_radiation_to_days(tilth : int,azimuth : int) -> List[float]:

    sorted_data_dict : dict = get_types_of_radiations_from_data(tilth,azimuth)

    times = pd.to_datetime(sorted_data_dict["time"])

    tf = TimezoneFinder()
    latitude, longitude = get_latitude_and_longitude()
    timezone_name :str = tf.timezone_at(lat = latitude, lng = longitude)

    times = times.tz_localize(timezone_name)
    location = Location(latitude,longitude,timezone_name)
    solar_positions = location.get_solarposition(times)

    data_total_radiation_hourly_hourly : List[float] = []

    for i in range(len(sorted_data_dict["ghi"])):

        total_radiation_on_hour :dict = pvlib.irradiance.get_total_irradiance(tilth,azimuth,
                                            solar_positions["zenith"].iloc[i],
                                            solar_positions["azimuth"].iloc[i],sorted_data_dict["dni"][i],
                                            sorted_data_dict["ghi"][i],sorted_data_dict["dhi"][i])

        data_total_radiation_hourly_hourly.append(float(total_radiation_on_hour["poa_global"]))

    data_total_radiation_hourly_by_day : List[float] = []

    for i in range(0, len(data_total_radiation_hourly_hourly), 24):
        soucet : float = sum(data_total_radiation_hourly_hourly[i:i+24])
        data_total_radiation_hourly_by_day.append(soucet)

    return data_total_radiation_hourly_by_day


def calculate_radiation_to_square(tilth : int,azimuth : int,square_metears : int ) -> float:

    data_total_radiation_hourly_by_day : List[float] = calculate_radiation_to_days(tilth,azimuth)

    for i in range(len(data_total_radiation_hourly_by_day)):
        data_total_radiation_hourly_by_day[i] *= square_metears

    return sum(data_total_radiation_hourly_by_day)



def calculate_total_radiation_all_areas(tilts : List[int], azimuths : List[int], areas: List[int])-> List[float] :

    radiatin_in_areas : List[float] = []

    for i in range(len(tilts)):
        radiatin_in_areas.append(calculate_radiation_to_square(tilts[i],azimuths[i],areas[i]))


    return radiatin_in_areas

def main_run():
    number_of_areas : int  = int(input("Kolik stran má objekt: "))

    tilts: List[int] = list()  # list uhlu
    azimuths: List[int] = list()  # list orientace
    areas: List[int] = list()

    for i in range(number_of_areas):
        number_of_areas_now : str = str(i + 1)
        tilt,azimuth,area = map(int, input
        ("Zadejte pro stranu "+ number_of_areas_now +
         " následující parametry oddělené mezerou vše v základních jednotkách: úhel sklonu, orientace a velikost plochy.")
                                      .split())
        tilts.append(tilt)
        azimuths.append(azimuth)
        areas.append(area)


    radiation_by_areas: List[float] = calculate_total_radiation_all_areas(tilts,azimuths,areas)

    for i in range(len(radiation_by_areas)):
        number_of_area_now: str = str(i + 1)
        print("Na plochu "+ number_of_area_now +" působí:"+ str(round(radiation_by_areas[i],2)) + "W.")

    print("Celkově na objekt působí: "+ str(round(sum(radiation_by_areas),2)) + "W.")

main_run()



