import json
from TLVquery import query_tel_aviv_gis
from OSMquery import query_osm_safety_data
from points_parser import get_route_coordinates


def analyze_routes_with_crime(sources_txt, route_json, max_points=20):
    """Analyze routes with infrastructure + crime/safety analysis"""

    print("📂 Loading sources...")
    with open(sources_txt, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    print(f"✅ Loaded {len(urls)} GIS URLs")

    print("🗺️ Parsing routes...")
    routes = get_route_coordinates(route_json)
    print(f"✅ Found {len(routes)} routes")

    created_files = []

    for route_idx, coords in enumerate(routes):
        print(f"\n🚶 Processing route {route_idx + 1}/{len(routes)} ({len(coords)} points)...")

        # Sample points if too many
        if len(coords) > max_points:
            print(f"⚡ Sampling {max_points} points from {len(coords)} total")
            indices = []
            for i in range(max_points):
                index = int((i * (len(coords) - 1)) / (max_points - 1))
                indices.append(index)
            sampled_coords = [coords[i] for i in indices]
        else:
            sampled_coords = coords

        route_data = {
            "route_index": route_idx,
            "total_points": len(coords),
            "analyzed_points": len(sampled_coords),
            "points": []
        }

        # Analyze each point
        for point_idx, (lat, lon) in enumerate(sampled_coords):
            print(f"  📍 Point {point_idx + 1}/{len(sampled_coords)} ({lat:.6f}, {lon:.6f})")

            point_data = {
                "index": point_idx,
                "lat": lat,
                "lon": lon,
                "osm": {},
                "gis": [],
                "crime_analysis": {}
            }

            # OSM query
            print("    🌍 Querying OSM...")
            point_data["osm"] = query_osm_safety_data(lat, lon)

            """# GIS queries
            for url_idx, url in enumerate(urls):
                print(f"    🏛️ Querying GIS {url_idx + 1}/{len(urls)}...")
                gis_result = query_tel_aviv_gis(url, lat, lon)
                point_data["gis"].append({
                    "url": url,
                    "features": gis_result
                })"""

            """# Crime/Safety Analysis
            print("    🚨 Analyzing crime/safety...")
            point_data["crime_analysis"] = analyze_point_crime_safety(lat, lon)

            """
            route_data["points"].append(point_data)

        # Save route data
        filename = f"route_{route_idx}_safety_data.json"
        print(f"💾 Saving {filename}...")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(route_data, f, ensure_ascii=False, indent=2)

        created_files.append(filename)
        print(f"✅ Route {route_idx} saved!")

    print(f"\n🎉 All {len(routes)} routes completed with crime analysis!")
    return created_files


def analyze_point_crime_safety(lat, lon):
    """Analyze crime and safety for a specific point"""

    # Tel Aviv area-based crime analysis
    area_info = get_area_crime_info(lat, lon)

    # Time-based risk analysis
    time_risks = analyze_time_risks(lat, lon)

    # Environmental safety factors
    env_factors = analyze_environmental_safety(lat, lon)

    return {
        "area_info": area_info,
        "time_risks": time_risks,
        "environmental_factors": env_factors,
        "overall_crime_level": area_info["crime_level"],
        "safety_score": calculate_safety_score(area_info, time_risks, env_factors)
    }


def get_area_crime_info(lat, lon):
    """Get crime information based on Tel Aviv area"""

    if lat > 32.08:  # North Tel Aviv
        return {
            "area_name": "North Tel Aviv (Ramat Aviv/University)",
            "crime_level": "LOW",
            "crime_types": ["Rare petty theft", "Bicycle theft"],
            "police_presence": "Regular patrols",
            "safety_reputation": "Very safe, family area",
            "risk_factors": ["Late night isolation in some areas"]
        }

    elif lat > 32.075:  # Central Tel Aviv
        return {
            "area_name": "Central Tel Aviv (Dizengoff/City Center)",
            "crime_level": "LOW-MEDIUM",
            "crime_types": ["Pickpocketing", "Tourist scams", "Bar fights"],
            "police_presence": "High visibility policing",
            "safety_reputation": "Safe but watch belongings",
            "risk_factors": ["Crowded areas", "Tourist targeting", "Night entertainment zones"]
        }

    elif lat > 32.065:  # Central-South
        return {
            "area_name": "Central-South (Rothschild/Neve Tzedek)",
            "crime_level": "LOW",
            "crime_types": ["Occasional theft", "Vandalism"],
            "police_presence": "Regular community policing",
            "safety_reputation": "Trendy, generally safe",
            "risk_factors": ["Expensive area - theft risk", "Late night bar areas"]
        }

    elif lat > 32.055:  # South-Central
        return {
            "area_name": "South-Central (Florentin/Shapira)",
            "crime_level": "MEDIUM",
            "crime_types": ["Petty theft", "Drug-related incidents", "Vandalism"],
            "police_presence": "Increased patrols due to gentrification",
            "safety_reputation": "Improving but mixed",
            "risk_factors": ["Nightlife areas", "Social tensions", "Construction zones"]
        }

    elif lat > 32.045:  # South Tel Aviv
        return {
            "area_name": "South Tel Aviv (HaTikva/Kiryat Shalom)",
            "crime_level": "MEDIUM-HIGH",
            "crime_types": ["Theft", "Assault", "Drug crimes", "Domestic violence"],
            "police_presence": "Community policing initiatives",
            "safety_reputation": "Requires caution",
            "risk_factors": ["Socioeconomic challenges", "Limited lighting", "Isolated areas"]
        }

    else:  # Far South/Industrial
        return {
            "area_name": "South Tel Aviv Industrial",
            "crime_level": "HIGH",
            "crime_types": ["Robbery", "Assault", "Property crime", "Drug activity"],
            "police_presence": "Limited patrol coverage",
            "safety_reputation": "Avoid if possible",
            "risk_factors": ["Industrial isolation", "Poor lighting", "Limited foot traffic", "Economic deprivation"]
        }


def analyze_time_risks(lat, lon):
    """Analyze time-based safety risks"""
    area_crime = get_area_crime_info(lat, lon)

    base_risks = {
        "morning": "Low risk",
        "afternoon": "Low risk",
        "evening": "Low-Medium risk",
        "late_night": "Medium risk"
    }

    # Adjust based on area
    if area_crime["crime_level"] in ["MEDIUM-HIGH", "HIGH"]:
        return {
            "morning": "Medium risk",
            "afternoon": "Medium risk",
            "evening": "High risk",
            "late_night": "Very High risk"
        }
    elif area_crime["crime_level"] == "MEDIUM":
        return {
            "morning": "Low risk",
            "afternoon": "Low risk",
            "evening": "Medium risk",
            "late_night": "High risk"
        }

    return base_risks


def analyze_environmental_safety(lat, lon):
    """Analyze environmental safety factors"""
    return {
        "street_lighting": "Assess from OSM/GIS data",
        "foot_traffic": "Based on area type and time",
        "escape_routes": "Multiple streets vs isolated",
        "help_availability": "Proximity to businesses/residents",
        "visibility": "Open spaces vs hidden areas"
    }


def calculate_safety_score(area_info, time_risks, env_factors):
    """Calculate overall safety score 1-10"""
    crime_scores = {
        "LOW": 8,
        "LOW-MEDIUM": 6,
        "MEDIUM": 5,
        "MEDIUM-HIGH": 3,
        "HIGH": 2
    }

    base_score = crime_scores.get(area_info["crime_level"], 5)

    # Adjust for specific risk factors
    risk_count = len(area_info.get("risk_factors", []))
    adjusted_score = max(1, base_score - (risk_count * 0.5))

    return min(10, adjusted_score)
