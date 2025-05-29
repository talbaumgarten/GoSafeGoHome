import json


def get_route_coordinates(json_file):
    """Extract list of routes, each route is list of (lat, lon) coordinates"""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)

        routes = []
        for route in data['routes']:
            coords = []
            for lon, lat in route['geometry']['coordinates']:
                coords.append((lat, lon))
            routes.append(coords)

        return routes
    except:
        return []


# Usage:
if __name__ == "__main__":
    routes = get_route_coordinates(r"C:\Users\talba\PycharmProjects\GoSafe&GoHome\get_route\route_output.json")
    print(f"Found {len(routes)} routes")
