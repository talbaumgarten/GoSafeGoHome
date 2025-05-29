import json
from TLVquery import query_tel_aviv_gis
from OSMquery import query_osm_safety_data
from points_parser import get_route_coordinates


def analyze_routes(sources_txt, route_json):
    """Extract all data for each route and save as JSON"""

    print("📂 Loading sources...")
    # Load GIS URLs from sources file
    with open(sources_txt, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    print(f"✅ Loaded {len(urls)} GIS URLs")

    print("🗺️ Parsing routes...")
    # Get route coordinates
    routes = get_route_coordinates(route_json)
    print(f"✅ Found {len(routes)} routes")

    created_files = []

    # Process each route
    for route_idx, coords in enumerate(routes):
        print(f"\n🚶 Processing route {route_idx + 1}/{len(routes)} ({len(coords)} points)...")

        route_data = {
            "route_index": route_idx,
            "points": []
        }

        # Process each point
        for point_idx, (lat, lon) in enumerate(coords):
            print(f"  📍 Point {point_idx + 1}/{len(coords)} ({lat:.6f}, {lon:.6f})")

            point_data = {
                "index": point_idx,
                "lat": lat,
                "lon": lon,
                "osm": {},
                "gis": []
            }

            # OSM query
            print("    🌍 Querying OSM...")
            point_data["osm"] = query_osm_safety_data(lat, lon)

            # Query each GIS URL
            for url_idx, url in enumerate(urls):
                print(f"    🏛️ Querying GIS {url_idx + 1}/{len(urls)}...")
                gis_result = query_tel_aviv_gis(url, lat, lon)
                point_data["gis"].append({
                    "url": url,
                    "features": gis_result
                })

            route_data["points"].append(point_data)

        # Save route data
        filename = f"route_{route_idx}_data.json"
        print(f"💾 Saving {filename}...")
        with open(filename, 'w') as f:
            json.dump(route_data, f, indent=2)

        created_files.append(filename)
        print(f"✅ Route {route_idx} saved!")

    print(f"\n🎉 All {len(routes)} routes completed!")
    return created_files


# Usage
if __name__ == "__main__":
    files = analyze_routes("sources.txt", "route.json")
    print(f"📁 Created files: {files}")