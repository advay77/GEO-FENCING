from pydantic import BaseModel, Field
from typing import Optional
from app.models.geo import GeoPoint

class StationBase(BaseModel):
    name: str
    code: str

class StationCreate(StationBase):
    location: GeoPoint
    
    class Config:
        schema_extra = {
            "example": {
                "name": "New Delhi Railway Station",
                "code": "NDLS",
                "location": {
                    "type": "Point",
                    "coordinates": [77.2207, 28.6425]
                }
            }
        }

class StationUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[GeoPoint] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "New Delhi Railway Station (Main)",
                "location": {
                    "type": "Point",
                    "coordinates": [77.2207, 28.6425]
                }
            }
        }

class Station(StationBase):
    location: GeoPoint
    
    class Config:
        schema_extra = {
            "example": {
                "name": "New Delhi Railway Station",
                "code": "NDLS",
                "location": {
                    "type": "Point",
                    "coordinates": [77.2207, 28.6425]
                }
            }
        }
        
    @classmethod
    def from_mongo(cls, mongo_doc):
        if mongo_doc.get("_id"):
            mongo_doc["id"] = str(mongo_doc.pop("_id"))
        return cls(**mongo_doc)