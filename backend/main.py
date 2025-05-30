from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel
import const
import time
import coord_to_json 
import gemini.gemini as gemini



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
    for route in const.RESULTS:
        if route["start_address"].lower() == req.start.lower() and route["end_address"].lower() == req.end.lower():
            time.sleep(1)
            return route
    route_json = coord_to_json.coord_to_json(req.start, req.end)
    gemini_json = gemini.run(route_json)
    return gemini_json

