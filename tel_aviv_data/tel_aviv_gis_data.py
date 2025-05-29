import json
import requests
from shapely.geometry import LineString, Point
from pyproj import Transformer
from geopy.distance import distance as geopy_distance


def get_nearby_lights(route_coords):
    min_lon = min(p[0] for p in route_coords)
    max_lon = max(p[0] for p in route_coords)
    min_lat = min(p[1] for p in route_coords)
    max_lat = max(p[1] for p in route_coords)

    transformer_to_itm = Transformer.from_crs("EPSG:4326", "EPSG:2039", always_xy=True)
    xmin, ymin = transformer_to_itm.transform(min_lon, min_lat)
    xmax, ymax = transformer_to_itm.transform(max_lon, max_lat)

    url = "https://gisn.tel-aviv.gov.il/arcgis/rest/services/IView2/MapServer/543/query"
    params = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "json",
        "geometry": f"{xmin},{ymin},{xmax},{ymax}",
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects"
    }

    response = requests.get(url, params=params)
    features = response.json().get("features", [])

    transformer = Transformer.from_crs("EPSG:2039", "EPSG:4326", always_xy=True)
    return [
        transformer.transform(f["geometry"]["x"], f["geometry"]["y"])
        for f in features
    ]


def count_shelters_along_route(route_coords):
    transformer_to_itm = Transformer.from_crs("EPSG:4326", "EPSG:2039", always_xy=True)
    min_lon = min(p[0] for p in route_coords)
    max_lon = max(p[0] for p in route_coords)
    min_lat = min(p[1] for p in route_coords)
    max_lat = max(p[1] for p in route_coords)
    xmin, ymin = transformer_to_itm.transform(min_lon, min_lat)
    xmax, ymax = transformer_to_itm.transform(max_lon, max_lat)

    url = "https://gisn.tel-aviv.gov.il/arcgis/rest/services/IView2/MapServer/592/query"
    params = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "json",
        "geometry": f"{xmin},{ymin},{xmax},{ymax}",
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects"
    }

    response = requests.get(url, params=params)
    features = response.json().get("features", [])

    transformer = Transformer.from_crs("EPSG:2039", "EPSG:4326", always_xy=True)
    route_line = LineString(route_coords)
    buffer_degrees = 0.00025

    count = 0
    for feature in features:
        geom = feature.get("geometry", {})
        x = geom.get("x")
        y = geom.get("y")
        if x is not None and y is not None:
            lon, lat = transformer.transform(x, y)
            if route_line.buffer(buffer_degrees).contains(Point(lon, lat)):
                count += 1

    return count


def analyze_route(route_coords):
    sample_lights = get_nearby_lights(route_coords)

    lit_distance = 0.0
    dark_distance = 0.0
    buffer_meters = 25

    for i in range(len(route_coords) - 1):
        lon1, lat1 = route_coords[i]
        lon2, lat2 = route_coords[i + 1]
        segment_len_km = geopy_distance((lat1, lon1), (lat2, lon2)).km

        is_lit = any(
            geopy_distance((lat1, lon1), (lat, lon)).meters < buffer_meters or
            geopy_distance((lat2, lon2), (lat, lon)).meters < buffer_meters
            for lon, lat in sample_lights
        )

        if is_lit:
            lit_distance += segment_len_km
        else:
            dark_distance += segment_len_km

    if lit_distance == 0 and dark_distance == 0:
        ratio = "Undefined"
    elif lit_distance == 0:
        ratio = "Infinity (fully dark)"
    else:
        ratio = round(dark_distance / lit_distance, 2)

    shelters_count = count_shelters_along_route(route_coords)

    return {
        "Lit Distance (km)": round(lit_distance, 3),
        "Dark Distance (km)": round(dark_distance, 3),
        "Dark-to-Lit Ratio": ratio,
        "Shelters Count": shelters_count
    }


def analyze_all_routes(route_json_path):
    with open(route_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []
    for idx, route in enumerate(data.get("routes", [])):
        coords = route["geometry"]["coordinates"]
        stats = analyze_route(coords)
        stats["Route Index"] = idx
        results.append(stats)

    return json.dumps(results, ensure_ascii=False)
