import osmnx as ox

# הגדרת שם העיר
place_name = "Tel Aviv, Israel"

# הורדת רשת הכבישים
graph = ox.graph_from_place(place_name, network_type='all')

# המרת הגרף ל-GeoDataFrame
edges = ox.graph_to_gdfs(graph, nodes=False)

# הצגת העמודות הזמינות
print(edges.columns)
