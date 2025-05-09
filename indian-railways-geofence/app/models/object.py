from pydantic import BaseModel
from typing import Optional
from app.models.geo import GeoPoint

class ObjectBase(BaseModel):
    id: str
    type: str
    ownerId: str
    trainNumber: str
    coachId: str

class ObjectCreate(ObjectBase):
    location: GeoPoint
    
    class Config:
        schema_extra = {
            "example": {
                "id": "OBJ001",
                "type": "Luggage",
                "ownerId": "Rahul Sharma",
                "trainNumber": "12301",
                "coachId": "A1",
                "location": {
                    "type": "Point",
                    "coordinates": [77.1000, 28.5500]
                }
            }
        }

class ObjectUpdate(BaseModel):
    type: Optional[str] = None
    ownerId: Optional[str] = None
    trainNumber: Optional[str] = None
    coachId: Optional[str] = None
    location: Optional[GeoPoint] = None
    
    class Config:
        schema_extra = {
            "example": {
                "location": {
                    "type": "Point",
                    "coordinates": [77.1500, 28.6000]
                }
            }
        }

class Object(ObjectBase):
    location: GeoPoint
    
    class Config:
        schema_extra = {
            "example": {
                "id": "OBJ001",
                "type": "Luggage",
                "ownerId": "Rahul Sharma",
                "trainNumber": "12301",
                "coachId": "A1",
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