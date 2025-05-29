import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import json

ox.settings.use_cache = True
ox.settings.log_console = True

def addresses_to_coords(origin_address, destination_address):
    origin_point = ox.geocoder.geocode(origin_address)
    destination_point = ox.geocoder.geocode(destination_address)
    return origin_point, destination_point


def coord_to_json(origin, destination):
    # Convert addresses to coordinates
    origin, destination = addresses_to_coords(origin_address, destination_address)
    if not origin or not destination:
        print("Could not geocode one or both addresses.")
        return
    G = ox.graph_from_point(origin, dist=1500, network_type='walk', simplify=True)

    # Get nearest nodes
    orig_node = ox.distance.nearest_nodes(G, X=origin[1], Y=origin[0])
    dest_node = ox.distance.nearest_nodes(G, X=destination[1], Y=destination[0])

    # Calculate routes
    shortest_path = nx.shortest_path(G, orig_node, dest_node, weight='length')
    alternative_path = nx.shortest_path(G, orig_node, dest_node, weight=lambda u, v, d: edge_safety_weight(u, v, d))
    

    # fig, ax = ox.plot_graph_routes(G, [shortest_path, alternative_path],route_colors=['#FF0000', '#00FF00'], route_linewidth=6, node_size=0)
    # plt.show()


    # Build route geometries
    routes = []
    for idx, path in enumerate([shortest_path, alternative_path]):
        coords = []
        for node in path:
            point = G.nodes[node]
            coords.append([point['x'], point['y']])  # [longitude, latitude]

        routes.append({
            "route_index": idx,
            "geometry": {
                "coordinates": coords
            }
        })

    # Build the full JSON structure
    output = {
        "start_address": origin_address,
        "end_address": destination_address,
        "start_coordinates": [origin[1], origin[0]],  # [lon, lat]
        "end_coordinates": [destination[1], destination[0]],
        "total_routes": 2,
        "routes": routes
    }

    return json.dumps(output)    

# function to calculate safety score per edge
def edge_safety_weight(u, v, data):
    score = 0
    if data.get('lit') == 'yes':
        score += 1
        print(f"Edge {u} to {v} is lit")
    if data.get('sidewalk') in ['yes', 'both']:
        score += 1
        print(f"Edge {u} to {v} has a sidewalk")
    if data.get('highway') in ['residential', 'living_street', 'pedestrian', 'footway']:
        score += 1
        print(f"Edge {u} to {v} is a safe highway type")
    # Higher score = safer => to make it a weight, we return the *inverse*
    return 1 / (score + 1)  # +1 to avoid division by zero


if __name__ == "__main__":
    origin_address = "Jaffa Flea Market Tel Aviv"        # Bugrashov Beach
    destination_address = "Carmel Market Tel Aviv"   # Sarona Market
    output_path = 'routes.json'

    json_obj = coord_to_json(origin_address, destination_address)
    print(f"JSON output:\n{json_obj}")
    
    