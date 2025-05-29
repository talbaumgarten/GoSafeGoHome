import json


def get_route_coordinates(json_file):
    """Extract list of routes, each route is list of (lat, lon) coordinates"""
    print(f"🔍 DEBUG: Starting to parse {json_file}")

    try:
        print(f"📂 Opening file: {json_file}")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"📊 JSON keys found: {list(data.keys())}")

        if 'routes' not in data:
            print("❌ ERROR: No 'routes' key found!")
            print(f"Available keys: {list(data.keys())}")
            return []

        routes_data = data['routes']
        print(f"🛣️ Found {len(routes_data)} routes in data")

        routes = []
        for i, route in enumerate(routes_data):
            print(f"📍 Processing route {i}")
            print(f"Route {i} keys: {list(route.keys())}")

            coords = []

            if 'geometry' not in route:
                print(f"❌ Route {i} missing 'geometry' key")
                continue

            geometry = route['geometry']
            print(f"Geometry keys: {list(geometry.keys())}")

            if 'coordinates' not in geometry:
                print(f"❌ Route {i} missing 'coordinates' in geometry")
                continue

            coordinate_list = geometry['coordinates']
            print(f"🗺️ Route {i} has {len(coordinate_list)} coordinate points")

            # Show first few coordinates for debugging
            if len(coordinate_list) > 0:
                print(f"First coordinate: {coordinate_list[0]}")
                print(f"Last coordinate: {coordinate_list[-1]}")

            for lon, lat in coordinate_list:
                coords.append((lat, lon))

            print(f"✅ Route {i}: converted {len(coords)} coordinates")
            routes.append(coords)

        print(f"🎉 SUCCESS: Processed {len(routes)} routes total")
        return routes

    except FileNotFoundError:
        print(f"❌ ERROR: File {json_file} not found!")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in {json_file}: {e}")
        return []
    except Exception as e:
        print(f"❌ ERROR: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return []

