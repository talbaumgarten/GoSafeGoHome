import google.generativeai as genai
import google.auth
import os
import json

class Gemini:
    """
    Gemini API client using the gemini-2.5-flash-preview-05-20 model.
    Use load_sources_from_txt() and load_route_from_json() to provide context, then call ask().
    """

    _SERVICE_ACCOUNT_FILE_PATH = r"hackathon-team-37_gemini.json"
    _DEFAULT_MODEL = "gemini-2.5-flash-preview-05-20"

    def __init__(self):
        self._route_description = ""
        self._source_context = ""
        self.model = None
        self.chat = None
        self.model_name = self._DEFAULT_MODEL
        self._initialized = False

    def init_model(self):
        try:
            print(f"Initializing model: {self.model_name}...")

            if not self._SERVICE_ACCOUNT_FILE_PATH:
                raise ValueError("Service account file path is not set.")

            credentials, _ = google.auth.load_credentials_from_file(self._SERVICE_ACCOUNT_FILE_PATH)
            genai.configure(credentials=credentials)

            self.model = genai.GenerativeModel(self.model_name)
            self.chat = self.model.start_chat()
            self._initialized = True

            print(f"Gemini {self.model_name} is ready!")
            return self

        except Exception as e:
            raise Exception(f"Failed to initialize Gemini: {e}")

    def load_sources_from_txt(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Source file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            self._source_context = f.read().strip()

        print(f"✅ Loaded sources from: {filepath}")

    def load_route_from_json(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Route file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            route_data = json.load(f)

        try:
            steps = route_data["routes"][0]["steps"]
            readable_steps = "\n".join(
                [f"- {step['instruction']} (Street: {step['street_name']}, Distance: {step['distance_meters']}m)"
                 for step in steps]
            )
            self._route_description = (
                f"Start: {route_data['start_address']}\n"
                f"End: {route_data['end_address']}\n"
                f"Total distance: {route_data['routes'][0]['distance_km']} km\n"
                f"Route steps:\n{readable_steps}"
            )
            print("✅ Loaded route from JSON.")
        except KeyError as e:
            raise ValueError(f"Missing expected key in JSON: {e}")

    def ask(self, question, short_answer=True):
        if not self._initialized:
            raise Exception("Model not initialized. Call init_model() first.")

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        try:
            prompt = ""

            if self._source_context:
                prompt += f"Based on the following sources:\n{self._source_context}\n\n"

            if self._route_description:
                prompt += (
                    f"Please evaluate the safety of the following route based only on the sources above.\n"
                    f"{self._route_description}\n\n"
                )

            prompt += question

            if short_answer:
                prompt += "\n\nPlease answer concisely."

            response = self.chat.send_message(prompt)
            return response.text

        except Exception as e:
            raise Exception(f"Error getting response: {e}")

    def get_model_name(self):
        return self.model_name if self._initialized else None


def main():
    gemini = Gemini()
    gemini.init_model()
    gemini.load_sources_from_txt("sources.txt")
    gemini.load_route_from_json("route.json")

    response = gemini.ask(
        "Score the route from 1 (unsafe) to 10 (very safe), and explain the reasoning using only the sources provided.",
        short_answer=False
    )
    print(response)


if __name__ == "__main__":
    main()
