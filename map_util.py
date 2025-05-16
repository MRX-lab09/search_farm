import math


def calculate_spn(toponym):
    envelope = toponym["boundedBy"]["Envelope"]
    lower_corner = envelope["lowerCorner"].split()
    upper_corner = envelope["upperCorner"].split()

    width = abs(float(upper_corner[0]) - float(lower_corner[0]))
    height = abs(float(upper_corner[1]) - float(lower_corner[1]))

    return f"{width},{height}"


def calculate_center_and_zoom(point1, point2):
    lon1, lat1 = map(float, point1.split(','))
    lon2, lat2 = map(float, point2.split(','))

    center_lon = (lon1 + lon2) / 2
    center_lat = (lat1 + lat2) / 2

    distance = math.sqrt((lon2 - lon1) ** 2 + (lat2 - lat1) ** 2)
    if distance < 0.01:
        spn = distance * 2
    else:
        spn = distance * 1.2

    return f"{center_lon},{center_lat}", f"{spn},{spn}"


def format_snippet(pharmacy_data, distance):
    name = pharmacy_data.get('name', 'Не указано')
    address = pharmacy_data.get('address', 'Не указано')
    hours = pharmacy_data.get('Hours', {}).get('text', 'Не указано')

    return f"""
Аптека: {name}
Адрес: {address}
Режим работы: {hours}
Расстояние: {distance:.2f} км
"""
