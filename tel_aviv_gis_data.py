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


def check_proximity_to_layer(route_coords, layer_id, strict_intersection=False):
    transformer_to_itm = Transformer.from_crs("EPSG:4326", "EPSG:2039", always_xy=True)
    min_lon = min(p[0] for p in route_coords)
    max_lon = max(p[0] for p in route_coords)
    min_lat = min(p[1] for p in route_coords)
    max_lat = max(p[1] for p in route_coords)
    xmin, ymin = transformer_to_itm.transform(min_lon, min_lat)
    xmax, ymax = transformer_to_itm.transform(max_lon, max_lat)

    url = f"https://gisn.tel-aviv.gov.il/arcgis/rest/services/IView2/MapServer/{layer_id}/query"
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

    for feature in features:
        geom = feature.get("geometry", {})
        x = geom.get("x")
        y = geom.get("y")
        if x is not None and y is not None:
            lon, lat = transformer.transform(x, y)
            point = Point(lon, lat)
            if strict_intersection:
                if route_line.intersects(point):
                    return True
            else:
                if route_line.buffer(buffer_degrees).contains(point):
                    return True
    return False


def count_items_along_route(route_coords, layer_id):
    transformer_to_itm = Transformer.from_crs("EPSG:4326", "EPSG:2039", always_xy=True)
    min_lon = min(p[0] for p in route_coords)
    max_lon = max(p[0] for p in route_coords)
    min_lat = min(p[1] for p in route_coords)
    max_lat = max(p[1] for p in route_coords)
    xmin, ymin = transformer_to_itm.transform(min_lon, min_lat)
    xmax, ymax = transformer_to_itm.transform(max_lon, max_lat)

    url = f"https://gisn.tel-aviv.gov.il/arcgis/rest/services/IView2/MapServer/{layer_id}/query"
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
            point = Point(lon, lat)
            if route_line.buffer(buffer_degrees).contains(point):
                count += 1
    return count


def count_shelters_along_route(route_coords):
    return count_items_along_route(route_coords, 592)


def is_near_construction(route_coords):
    return check_proximity_to_layer(route_coords, 479)


def is_near_night_public_work(route_coords):
    return check_proximity_to_layer(route_coords, 858)


def is_near_road_work(route_coords):
    return check_proximity_to_layer(route_coords, 852)


def is_on_walking_street(route_coords):
    return check_proximity_to_layer(route_coords, 659, strict_intersection=True)


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

    return {
        "Lit Distance (km)": round(lit_distance, 3),
        "Dark Distance (km)": round(dark_distance, 3),
        "Dark-to-Lit Ratio": ratio,
        "Shelters Count": count_shelters_along_route(route_coords),
        "Near Construction Site": is_near_construction(route_coords),
        "Near Night Construction Work": is_near_night_public_work(route_coords),
        "Near Road Work": is_near_road_work(route_coords),
        "On Walking Street": is_on_walking_street(route_coords)
    }


def analyze_all_routes_from_json_obj(route_data):
    results = []
    for idx, route in enumerate(route_data.get("routes", [])):
        coords = route["geometry"]["coordinates"]
        stats = analyze_route(coords)
        stats["Route Index"] = idx
        results.append(stats)
    return json.dumps(results, ensure_ascii=False)
