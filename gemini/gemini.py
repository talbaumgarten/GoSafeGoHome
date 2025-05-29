import osmnx as ox
import pandas as pd
import google.generativeai as genai
import google.auth
import os
import json


class Gemini:
    _SERVICE_ACCOUNT_FILE_PATH = r"hackathon-team-37_gemini.json"
    _DEFAULT_MODEL = "gemini-2.5-flash-preview-05-20"

    def __init__(self):
        self._routes = None
        self._source_context = ""
        self.model = None
        self.chat = None
        self.model_name = self._DEFAULT_MODEL
        self._initialized = False

    def init_model(self):
        print(f"Initializing model: {self.model_name}...")
        credentials, _ = google.auth.load_credentials_from_file(self._SERVICE_ACCOUNT_FILE_PATH)
        genai.configure(credentials=credentials)
        self.model = genai.GenerativeModel(self.model_name)
        self.chat = self.model.start_chat()
        self._initialized = True
        print(f"Gemini {self.model_name} is ready!")
        return self

    def load_sources_from_txt(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Source file not found: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            self._source_context = f.read().strip()
        print(f"✅ Loaded sources from: {filepath}")

    def load_routes_from_json(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Route file not found: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._routes = []

        for route in data["routes"]:
            index = route["route_index"]
            coords = route.get("geometry", {}).get("coordinates", [])
            enriched = self._enrich_coordinates_with_osm(coords)

            # Debug print: show enriched metadata per coordinate
            print(f"\n🔍 Enriched data for Route {index}:")
            for p in enriched:
                print(
                    f"  Point {p['index']} @ ({p['lat']:.6f}, {p['lon']:.6f}) → "
                    f"lit: {p.get('lit')}, surface: {p.get('surface')}, "
                    f"width: {p.get('width')}, cycleway: {p.get('cycleway')}, "
                    f"error: {p.get('error', 'None')}"
                )

            self._routes.append({
                "index": index,
                "description": self._format_route_description(data, route, enriched)
            })

        print(f"✅ Loaded {len(self._routes)} route(s) with OSM metadata.")

    def _enrich_coordinates_with_osm(self, coords, buffer_meters=25):
        enriched = []
        tags = {"lit": True, "surface": True, "width": True, "cycleway": True}

        for i, (lon, lat) in enumerate(coords):
            try:
                gdf = ox.features_from_point((lat, lon), tags=tags, dist=buffer_meters)

                if gdf.empty:
                    enriched.append({
                        "index": i, "lat": lat, "lon": lon,
                        "lit": None, "surface": None,
                        "width": None, "cycleway": None
                    })
                    continue

                # Try to find the first row with at least one of the desired columns
                row = \
                gdf.loc[:, gdf.columns.intersection(["lit", "surface", "width", "cycleway"])].dropna(how='all').iloc[0]

                enriched.append({
                    "index": i,
                    "lat": lat,
                    "lon": lon,
                    "lit": row.get("lit") if pd.notna(row.get("lit")) else None,
                    "surface": row.get("surface") if pd.notna(row.get("surface")) else None,
                    "width": row.get("width") if pd.notna(row.get("width")) else None,
                    "cycleway": row.get("cycleway") if pd.notna(row.get("cycleway")) else None
                })

            except Exception as e:
                enriched.append({
                    "index": i,
                    "lat": lat,
                    "lon": lon,
                    "lit": None, "surface": None,
                    "width": None, "cycleway": None,
                    "error": str(e)
                })

        return enriched

    def _format_route_description(self, data, route, enriched_data):
        lines = [
            f"Route {route['route_index']}:",
            f"Start address: {data['start_address']}",
            f"End address: {data['end_address']}",
            f"Total distance: {route['distance_km']} km",
            "Route coordinates with OSM metadata:"
        ]
        for p in enriched_data:
            lines.append(
                f"- Point {p['index']}: ({p['lat']:.6f}, {p['lon']:.6f}), "
                f"lit: {p.get('lit')}, surface: {p.get('surface')}, "
                f"width: {p.get('width')}, cycleway: {p.get('cycleway')}"
            )
        return "\n".join(lines)

    def ask(self, question, short_answer=True):
        if not self._initialized:
            raise Exception("Model not initialized. Call init_model() first.")
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")
        results = []
        for route in self._routes:
            prompt = ""
            if self._source_context:
                prompt += f"Based on the following sources:\n{self._source_context}\n\n"
            prompt += f"{route['description']}\n\n"
            prompt += question
            if short_answer:
                prompt += "\n\nPlease answer concisely."
            response = self.chat.send_message(prompt)
            results.append((route['index'], response.text))
        return results

    def get_model_name(self):
        return self.model_name if self._initialized else None


def main():
    gemini = Gemini()
    gemini.init_model()
    gemini.load_sources_from_txt("sources.txt")
    gemini.load_routes_from_json(r"C:\\Users\\talba\\PycharmProjects\\GoSafe&GoHome\\get_route\\route_output.json")
    results = gemini.ask(
        "Score the route from 1 (unsafe) to 10 (very safe), and explain the reasoning using only the sources provided.",
        short_answer=True
    )
    for index, answer in results:
        print(f"\n🚣️ Route {index} Safety Evaluation:\n{answer}")


if __name__ == "__main__":
    main()
