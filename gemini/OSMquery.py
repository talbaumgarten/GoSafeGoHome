import osmnx as ox
import pandas as pd


def query_osm_safety_data(lat: float, lon: float, radius_meters: int = 100):
    """
    Query OSM for safety-related features around coordinates

    Args:
        lat: Latitude
        lon: Longitude
        radius_meters: Search radius

    Returns:
        Dictionary with safety data or empty dict if error
    """
    try:
        # Safety-related tags to query
        tags = {
            "lit": True,
            "surface": True,
            "width": True,
            "highway": True,
            "footway": True,
            "sidewalk": True,
            "crossing": True,
            "barrier": True,
            "amenity": True
        }

        # Get features from OSM
        gdf = ox.features_from_point((lat, lon), tags=tags, dist=radius_meters)

        if gdf.empty:
            return {}

        # Extract relevant data
        result = {}
        for tag in tags.keys():
            if tag in gdf.columns:
                values = gdf[tag].dropna().unique()
                if len(values) > 0:
                    result[tag] = values.tolist()

        # Add feature count
        result['total_features'] = len(gdf)

        return result

    except:
        return {}

