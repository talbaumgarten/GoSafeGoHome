import json
import sys
from mapbox import Directions, Geocoder

class MapboxWalkingRouter:
    def __init__(self, access_token: str):
        self.directions = Directions(access_token=access_token)
        self.geocoder = Geocoder(access_token=access_token)
    
    def get_coordinates(self, address: str):
        """Convert address to coordinates."""
        try:
            response = self.geocoder.forward(address, limit=1)
            if response.status_code == 200:
                data = response.json()
                if data.get('features'):
                    coords = data['features'][0]['geometry']['coordinates']
                    return (coords[0], coords[1])  # longitude, latitude
            return None
        except:
            return None
    
    def get_walking_route(self, start_address: str, end_address: str):
        """Get walking route between two addresses with alternative routes."""
        # Get coordinates for both addresses
        start_coords = self.get_coordinates(start_address)
        if not start_coords:
            return {"error": "Could not find start address"}
        
        end_coords = self.get_coordinates(end_address)
        if not end_coords:
            return {"error": "Could not find end address"}
        
        try:
            # Create features for the API
            features = [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [start_coords[0], start_coords[1]]
                    }
                },
                {
                    "type": "Feature", 
                    "geometry": {
                        "type": "Point",
                        "coordinates": [end_coords[0], end_coords[1]]
                    }
                }
            ]
            
            # Get route with alternatives and Hebrew language support
            response = self.directions.directions(
                features,
                profile='mapbox.walking',
                geometries='geojson',
                steps=True,
                overview='full',
                alternatives=True,
                language='en'  # Hebrew language for street names
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('routes'):
                    return self._format_routes(data['routes'], start_address, end_address, start_coords, end_coords)
                else:
                    return {"error": "No route found"}
            else:
                return {"error": "API request failed"}
                
        except:
            return {"error": "Route calculation failed"}
    
    def _format_routes(self, routes, start_address, end_address, start_coords, end_coords):
        """Format multiple route data for output."""
        formatted_routes = []
        
        for i, route in enumerate(routes):
            distance_meters = route.get('distance', 0)
            duration_seconds = route.get('duration', 0)
            
            # Extract steps with Hebrew street names
            steps = []
            if 'legs' in route and route['legs']:
                for leg in route['legs']:
                    if 'steps' in leg:
                        for step in leg['steps']:
                            maneuver = step.get('maneuver', {})
                            step_data = {
                                'instruction': maneuver.get('instruction', ''),
                                'distance_meters': step.get('distance', 0),
                                'duration_seconds': step.get('duration', 0)
                            }
                            
                            # Add street names in Hebrew if available
                            if 'name' in step:
                                step_data['street_name'] = step['name']
                            if 'ref' in step:
                                step_data['street_ref'] = step['ref']
                            if 'destinations' in step:
                                step_data['destinations'] = step['destinations']
                            
                            steps.append(step_data)
            
            formatted_route = {
                'route_index': i,
                'distance_meters': distance_meters,
                'distance_km': round(distance_meters / 1000, 2),
                'duration_seconds': duration_seconds,
                'duration_minutes': round(duration_seconds / 60, 1),
                'geometry': route.get('geometry'),
                'steps': steps
            }
            
            formatted_routes.append(formatted_route)
        
        return {
            'start_address': start_address,
            'end_address': end_address,
            'start_coordinates': start_coords,
            'end_coordinates': end_coords,
            'total_routes': len(formatted_routes),
            'routes': formatted_routes
        }

def load_input(filename='input.json'):
    """Load input from JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def save_output(data, filename='route_output.json'):
    """Save route data to JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

def main():
    # Load configuration
    config = load_input('config.json')
    if not config or 'access_token' not in config:
        print("Error: config.json missing or no access_token")
        sys.exit(1)
    
    # Initialize router
    router = MapboxWalkingRouter(config['access_token'])
    
    # Load input data
    input_data = load_input('input.json')
    if not input_data:
        print("Error: input.json not found or invalid")
        sys.exit(1)
    
    if 'start_address' not in input_data or 'end_address' not in input_data:
        print("Error: input.json must contain start_address and end_address")
        sys.exit(1)
    
    # Get route
    result = router.get_walking_route(
        input_data['start_address'], 
        input_data['end_address']
    )
    
    # Save output
    output_file = input_data.get('output_file', 'route_output.json')
    if save_output(result, output_file):
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Route saved to {output_file}")
    else:
        print("Error: Could not save output file")

if __name__ == "__main__":
    main()