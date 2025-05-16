import sys
import requests
from io import BytesIO
from PIL import Image
from map_utils import calculate_spn, calculate_center_and_zoom, format_snippet

GEOCODER_API_KEY = "8013b162-6b42-4997-9691-77b7074026e0"
STATIC_MAPS_API_KEY = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
PLACES_API_KEY = "8013b162-6b42-4997-9691-77b7074026e0"


def geocode(address):
    geocoder_url = "http://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": GEOCODER_API_KEY,
        "geocode": address,
        "format": "json"
    }
    response = requests.get(geocoder_url, params=params)
    if not response.ok:
        raise Exception(f"Geocoder error: {response.status_code}")

    json_data = response.json()
    try:
        toponym = json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        coords = toponym["Point"]["pos"]
        return coords.replace(" ", ","), toponym
    except (KeyError, IndexError):
        raise Exception("Адрес не найден")


def find_nearest_pharmacy(coords):
    places_url = "https://search-maps.yandex.ru/v1/"
    params = {
        "apikey": PLACES_API_KEY,
        "text": "аптека",
        "lang": "ru_RU",
        "ll": coords,
        "type": "biz",
        "results": 1
    }
    response = requests.get(places_url, params=params)
    if not response.ok:
        raise Exception(f"Places API error: {response.status_code}")

    json_data = response.json()
    if not json_data.get("features"):
        raise Exception("Аптеки не найдены")

    feature = json_data["features"][0]
    pharmacy_coords = ",".join(map(str, feature["geometry"]["coordinates"]))
    properties = feature["properties"]

    return pharmacy_coords, properties


def calculate_distance(coords1, coords2):
    lon1, lat1 = map(float, coords1.split(','))
    lon2, lat2 = map(float, coords2.split(','))
    return math.sqrt((lon2 - lon1) ** 2 + (lat2 - lat1) ** 2) * 111


def show_map(point_coords, pharmacy_coords):
    center, spn = calculate_center_and_zoom(point_coords, pharmacy_coords)

    map_params = {
        "l": "map",
        "pt": f"{point_coords},pm2rdl~{pharmacy_coords},pm2gnl",
        "ll": center,
        "spn": spn,
        "apikey": STATIC_MAPS_API_KEY
    }

    map_url = "https://static-maps.yandex.ru/1.x/"
    response = requests.get(map_url, params=map_params)

    if response.ok:
        Image.open(BytesIO(response.content)).show()
    else:
        raise Exception(f"Map error: {response.status_code}")


def main():
    if len(sys.argv) < 2:
        print("Использование: python pharmacy_finder.py <адрес>")
        return

    address = " ".join(sys.argv[1:])

    try:
        point_coords, toponym = geocode(address)

        pharmacy_coords, pharmacy_data = find_nearest_pharmacy(point_coords)

        distance = calculate_distance(point_coords, pharmacy_coords)

        print(format_snippet(pharmacy_data, distance))

        show_map(point_coords, pharmacy_coords)

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    import math

    main()
