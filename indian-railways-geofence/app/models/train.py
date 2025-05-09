from pydantic import BaseModel, Field
from typing import List, Optional
from app.models.geo import GeoPoint

class Coach(BaseModel):
    id: str
    geofenceRadius: float = Field(0.05, description="Geo-fence radius in kilometers")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "A1",
                "geofenceRadius": 0.05
            }
        }

class TrainBase(BaseModel):
    name: str
    number: str
    speed: float = Field(80.0, description="Speed in km/h")
    direction: float = Field(0.0, description="Direction in degrees (0-360)")
    coaches: List[Coach]

class TrainCreate(TrainBase):
    location: GeoPoint
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Rajdhani Express",
                "number": "12301",
                "speed": 80.0,
                "direction": 0.0,
                "coaches": [
                    {"id": "A1", "geofenceRadius": 0.05},
                    {"id": "A2", "geofenceRadius": 0.05},
                    {"id": "B1", "geofenceRadius": 0.05}
                ],
                "location": {
                    "type": "Point",
                    "coordinates": [77.1000, 28.5500]
                }
            }
        }

class TrainUpdate(BaseModel):
    name: Optional[str] = None
    speed: Optional[float] = None
    direction: Optional[float] = None
    location: Optional[GeoPoint] = None
    coaches: Optional[List[Coach]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "speed": 90.0,
                "direction": 45.0,
                "location": {
                    "type": "Point",
                    "coordinates": [77.1500, 28.6000]
                }
            }
        }

class Train(TrainBase):
    location: GeoPoint
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Rajdhani Express",
                "number": "12301",
                "speed": 80.0,
                "direction": 0.0,
                "coaches": [
                    {"id": "A1", "geofenceRadius": 0.05},
                    {"id": "A2", "geofenceRadius": 0.05},
                    {"id": "B1", "geofenceRadius": 0.05}
                ],
                "location": {
                    "type": "Point",
                    "coordinates": [77.1000, 28.5500]
                }
            }
        }
    
    @classmethod
    def from_mongo(cls, mongo_doc):
        if mongo_doc.get("_id"):
            mongo_doc["id"] = str(mongo_doc.pop("_id"))
        return cls(**mongo_doc)