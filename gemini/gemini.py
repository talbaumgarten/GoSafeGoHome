import json
import google.generativeai as genai
import google.auth


def score_route_safety(input_json, gemini_key_file="hackathon-team-37_gemini.json"):
    """Score route safety using Gemini AI"""

    # Initialize Gemini
    credentials, _ = google.auth.load_credentials_from_file(gemini_key_file)
    genai.configure(credentials=credentials)
    # Using 'gemini-1.5-flash' for better JSON handling and longer context
    model = genai.GenerativeModel("gemini-1.5-flash")

    results = []
    # Process each route file
    for route_data in input_json:

        # Convert route_data to a JSON string
        route_data_json_string = json.dumps(route_data, indent=2)  # Added indent for readability in prompt

        # Create prompt
        prompt = create_safety_prompt(route_data["Route Index"],
                                      route_data_json_string)  # Pass JSON string to prompt function

        # Get Gemini response
        # Pass only the prompt string to generate_content
        response = model.generate_content(prompt)

        # Parse response
        route_score = parse_gemini_response(response.text, route_data["Route Index"])

        results.append(route_score)

    return results


def create_safety_prompt(route_idx, route_data_json_string):  # Updated to accept JSON string
    """Create safety analysis prompt for Gemini"""

    prompt = f"""
    Analyze the safety of walking route {route_idx} based on the following JSON data:

    ```json
    {route_data_json_string}
    ```

    INSTRUCTIONS:
    Rate this walking route's safety from 1 (very unsafe) to 10 (very safe) according the data and web searching.
        
    Lit Distance (km): means a longer lit distance improves visibility and makes the route safer at night
    Dark Distance (km): means a shorter dark distance is safer, as unlit areas can pose risks
    Dark-to-Lit Ratio: means a lower ratio indicates a safer, better-lit route overall
    Shelters Count: means more shelters along the route offer better protection and comfort
    Near Construction Site: means routes away from construction zones are generally safer and less disruptive
    Near Night Public Work: means avoiding night public works reduces exposure to noise and temporary hazards
    Near Road Work: means it's safer to take routes that don't pass near active roadwork
    On Walking Street: means routes on pedestrian-only streets are safer and more comfortable for walking


    RESPONSE FORMAT:
    Route: [route number]
    Score: [number]/10
    Analysis: [max 20 words explaining the score, focusing on key safety aspects]
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


if __name__ == "__main__":

    route_json = r"C:\Users\talba\PycharmProjects\GoSafe&GoHome\get_route\route_output_2.json"
    with open(route_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    nitsan1 = r"nitsan.json"

    with open(nitsan1, "r", encoding="utf-8") as f:
        data2 = json.load(f)

    scores = score_route_safety(data2)

    for result in scores:
        for i in range(len(data["routes"])):
            if data["routes"][i]["route_index"] == result["route"]:
                data["routes"][i]["safety_score"] = result["score"]
                print(result["score"])
                data["routes"][i]["safety_description"] = result["analysis"]
                print(result["analysis"])
