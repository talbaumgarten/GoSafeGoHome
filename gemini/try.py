import osmnx as ox
import pandas as pd

coords = [
    (32.065379, 34.776573),
    (32.066196, 34.776966),
    (32.067102, 34.777365),
    (32.068003, 34.777742),
    (32.068900, 34.778123)
]


def enrich_coords_osm(coords, buffer=30):
    enriched = []
    tags = {
        "highway": True,
        "lit": True,
        "surface": True,
        "sidewalk": True,
        "cycleway": True,
        "lanes": True,
        "maxspeed": True
    }

    for i, (lat, lon) in enumerate(coords):
        try:
            gdf = ox.features_from_point((lat, lon), tags=tags, dist=buffer)
            roads = gdf[gdf.geometry.geom_type == "LineString"]
            if not roads.empty:
                row = roads.iloc[0]
                enriched.append({
                    "index": i,
                    "lat": lat,
                    "lon": lon,
                    "highway": row.get("highway"),
                    "lit": row.get("lit"),
                    "surface": row.get("surface"),
                    "sidewalk": row.get("sidewalk"),
                    "cycleway": row.get("cycleway"),
                    "lanes": row.get("lanes"),
                    "maxspeed": row.get("maxspeed")
                })
            else:
                enriched.append({"index": i, "lat": lat, "lon": lon, "note": "No road data found"})
        except Exception as e:
            enriched.append({"index": i, "lat": lat, "lon": lon, "error": str(e)})

    return pd.DataFrame(enriched)


df = enrich_coords_osm(coords)
print(df)
