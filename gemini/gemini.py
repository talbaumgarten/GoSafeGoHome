import json
import os
import google.generativeai as genai
import google.auth


def score_route_safety(json_files, gemini_key_file="hackathon-team-37_gemini.json"):
    """Score route safety using Gemini AI"""

    # Initialize Gemini
    print("🤖 Initializing Gemini...")
    credentials, _ = google.auth.load_credentials_from_file(gemini_key_file)
    genai.configure(credentials=credentials)
    model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")

    results = []

    # Process each route file
    for file_path in json_files:
        print(f"📊 Analyzing {file_path}...")

        # Load route data
        with open(file_path, 'r', encoding='utf-8') as f:
            route_data = json.load(f)

        # Create prompt
        prompt = create_safety_prompt(route_data)

        # Get Gemini response
        response = model.generate_content(prompt)

        # Parse response
        route_score = parse_gemini_response(response.text, route_data["route_index"])

        results.append(route_score)
        print(f"✅ Route {route_data['route_index']}: Score {route_score['score']}/10")

    return results


def create_safety_prompt(route_data):
    """Create safety analysis prompt for Gemini"""

    route_idx = route_data["route_index"]
    total_points = len(route_data["points"])

    # Count safety features
    osm_features = sum(len(point["osm"]) for point in route_data["points"])
    gis_features = sum(len(point["gis"]) for point in route_data["points"])

    # Sample some points for detail
    sample_points = route_data["points"][:5]  # First 5 points

    prompt = f"""
Analyze the safety of walking route {route_idx} based on this data:

ROUTE OVERVIEW:
- Total points: {total_points}
- OSM safety features found: {osm_features}
- Tel Aviv GIS features found: {gis_features}

SAMPLE POINTS DATA:
"""

    for point in sample_points:
        prompt += f"""
Point {point['index']} ({point['lat']:.6f}, {point['lon']:.6f}):
- OSM data: {point['osm']}
- GIS features: {len([f for gis in point['gis'] for f in gis['features']])} total
"""

    prompt += """
INSTRUCTIONS:
Rate this walking route's safety from 1 (very unsafe) to 10 (very safe).
Consider: lighting, surface quality, sidewalks, security cameras, municipal facilities.

RESPONSE FORMAT:
Route: [route number]
Score: [number]/10
Analysis: [max 20 words explaining the score]
"""

    return prompt


def parse_gemini_response(response_text, route_index):
    """Parse Gemini response to extract score and analysis"""

    # Extract score
    score = 5  # default
    lines = response_text.strip().split('\n')

    for line in lines:
        if 'Score:' in line or 'score:' in line:
            try:
                score_part = line.split(':')[1].strip()
                score = int(score_part.split('/')[0])
                break
            except:
                pass

    # Extract analysis
    analysis = ""
    capture = False
    for line in lines:
        if 'Analysis:' in line or 'analysis:' in line:
            analysis = line.split(':', 1)[1].strip()
            capture = True
        elif capture and line.strip():
            analysis += " " + line.strip()

    if not analysis:
        analysis = response_text[:200] + "..." if len(response_text) > 200 else response_text

    return {
        "route": route_index,
        "score": score,
        "analysis": analysis.strip()
    }


# Usage
if __name__ == "__main__":
    from route_analyzer import analyze_routes_with_crime

    # Get route files from the analyzer
    route_files = analyze_routes_with_crime("sources.txt", r"C:\Users\talba\PycharmProjects\GoSafe&GoHome\get_route\route_output.json")

    # Score the routes
    scores = score_route_safety(route_files)

    print("\n🎯 SAFETY SCORES:")
    for result in scores:
        print(f"\nRoute {result['route']}: {result['score']}/10")
        print(f"Analysis: {result['analysis']}")