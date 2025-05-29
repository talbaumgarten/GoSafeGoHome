from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RouteRequest(BaseModel):
    start: str
    end: str

@app.post("/safe-route")
def get_safe_route(req: RouteRequest):
    # Dummy safe route logic
    return {
        "route": [
            {"lat": 40.748817, "lng": -73.985428},
            {"lat": 40.749017, "lng": -73.987428},
        ],
        "safety_score": 0.92
    }
