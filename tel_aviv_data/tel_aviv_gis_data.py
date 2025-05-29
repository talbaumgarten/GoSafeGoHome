import json
from shapely.geometry import LineString, Point
from pyproj import Transformer
import pandas as pd

# --- קריאת קובץ JSON עם המסלול ---
with open("route_output.json", "r", encoding="utf-8") as f:
    route_data = json.load(f)

# --- חילוץ הנ"צ מהקובץ ---
route_coords = route_data["routes"][0]["geometry"]["coordinates"]

# Simulated: route coordinates (WGS84)
route_coords = [
    [34.770606, 32.081301],
    [34.770709, 32.081496],
    [34.77074, 32.081562],
    [34.771088, 32.08228],
    [34.771106, 32.082369],
    [34.771816, 32.083775],
    [34.771956, 32.08407],
    [34.772351, 32.084823],
    [34.77239, 32.084915],
    [34.7725, 32.084997],
    [34.772664, 32.085461],
    [34.772704, 32.085574],
    [34.772884, 32.086192],
    [34.773219, 32.087301],
    [34.773163, 32.087416],
    [34.773234, 32.087639],
    [34.773304, 32.08785],
    [34.77352, 32.088608],
    [34.773475, 32.088622],
    [34.773358, 32.088658],
]
route_line = LineString(route_coords)

# Simulated street light locations (WGS84) - sample subset
sample_lights = [
    (34.7707, 32.0815),
    (34.7711, 32.0822),
    (34.7719, 32.0840),
    (34.7723, 32.0848),
    (34.7726, 32.0854),
    (34.7728, 32.0861),
    (34.7732, 32.0873),
    (34.7735, 32.0886),
    (34.7750, 32.0900),  # far from route
]

# Check how many lights are within ~25 meters of the path
buffer_degrees = 0.00025
count_on_route = sum(
    route_line.buffer(buffer_degrees).contains(Point(lon, lat))
    for lon, lat in sample_lights
)

# Route length (from your JSON input)
route_length_km = 0.88
density = round(count_on_route / route_length_km, 2)

# Result table
df = pd.DataFrame([{
    "Street Light Count": count_on_route,
    "Route Length (km)": route_length_km,
    "Lights per km": density
}])

print(df.to_string(index=False))

# Save output to JSON file
df.to_json("route_lighting_output.json", orient="records", indent=2)
print("✅ Data exported to route_lighting_output.json")
