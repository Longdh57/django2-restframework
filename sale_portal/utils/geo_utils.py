from math import sin, cos, sqrt, atan2, radians

import numpy as np

from sale_portal.geodata.models import GeoData


def findDistance(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c * 1000
    distance = round(distance)
    if distance < 1000:
        return {'text': str(distance) + 'm', 'value': distance}
    else:
        return {'text': str(distance / 1000) + 'km', 'value': distance}


def checkInside(code, latitude, longitude):
    code = str(code).zfill(5)
    polyPoints = GeoData.objects.filter(
        code=str(code)
    ).only('geojson')
    if len(polyPoints) == 0:
        return 1
    polyPoints = polyPoints[0].geojson.get('geometry').get('coordinates')[0][0]

    x = latitude
    y = longitude
    inside = False
    i = 0
    j = len(polyPoints) - 1

    while i < len(polyPoints):
        xi = polyPoints[i][1]
        yi = polyPoints[i][0]
        xj = polyPoints[j][1]
        yj = polyPoints[j][0]
        intersect = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi)
        if intersect:
            if inside:
                inside = False
            else:
                inside = True
        j = i
        i = i + 1

    if inside:
        return 1
    else:
        # check distance from point to polyPoints, Accept tolerances when auto generate and calculate on curved surfaces
        p1 = np.array([latitude, longitude])
        length = len(polyPoints)
        if length > 2:
            distance = 10000000000
            for k in range(0, length - 1):
                p2 = np.array([polyPoints[k][0], polyPoints[k][1]])
                p3 = np.array([polyPoints[k + 1][0], polyPoints[k + 1][1]])
                # Accept tolerances with constance 111195
                d = abs(np.cross(p2 - p1, p3 - p1) * 111195 / np.linalg.norm(p2 - p1))
                if d < distance:
                    distance = d
            if distance < 300:
                return 1
            else:
                return 0

        else:
            return -1
    return -1
