import requests
import math


def query_tel_aviv_gis(url: str, lat: float, lon: float, radius_meters: int = 100):
    """
    Query Tel Aviv GIS service with coordinates

    Args:
        url: GIS service URL
        lat: Latitude
        lon: Longitude
        radius_meters: Search radius

    Returns:
        List of features or empty list if error
    """
    try:
        # Create bounding box
        lat_buffer = radius_meters / 111000
        lon_buffer = radius_meters / (111000 * math.cos(math.radians(lat)))
        bbox = f"{lon - lon_buffer},{lat - lat_buffer},{lon + lon_buffer},{lat + lat_buffer}"

        # Query parameters
        params = {
            'where': '1=1',
            'geometry': bbox,
            'geometryType': 'esriGeometryEnvelope',
            'spatialRel': 'esriSpatialRelIntersects',
            'outFields': '*',
            'returnGeometry': 'true',
            'f': 'json',
            'inSR': '4326',
            'outSR': '4326'
        }

        # Execute query
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        return data.get('features', [])

    except:
        return []


# Usage example:
if __name__ == "__main__":
    # Test with security cameras
    url = "https://gisn.tel-aviv.gov.il/arcgis/rest/services/IView2/MapServer/543/query"
    lat, lon = 32.0853, 34.7818  # Dizengoff Center

    features = query_tel_aviv_gis(url, lat, lon)
    print(f"Found {len(features)} features")

    if features:
        print("First feature:", features[0])
