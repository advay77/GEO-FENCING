from pydantic import BaseModel
from typing import List, Literal

class GeoPoint(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: List[float]  # [longitude, latitude]
    
    class Config:
        schema_extra = {
            "example": {
                "type": "Point",
                "coordinates": [77.2207, 28.6425]
            }
        }