from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class AlertBase(BaseModel):
    type: Literal["station_proximity", "theft"]
    trainNumber: str
    trainName: str
    resolved: bool = False

class AlertCreate(AlertBase):
    timestamp: datetime = Field(default_factory=datetime.now)
    # For station alerts
    stationCode: Optional[str] = None
    stationName: Optional[str] = None
    distance: Optional[float] = None  # in kilometers
    # For theft alerts
    objectId: Optional[str] = None
    objectType: Optional[str] = None
    ownerId: Optional[str] = None
    coachId: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "type": "station_proximity",
                "trainNumber": "12301",
                "trainName": "Rajdhani Express",
                "stationCode": "NDLS",
                "stationName": "New Delhi Railway Station",
                "distance": 0.85
            }
        }

class AlertUpdate(BaseModel):
    resolved: Optional[bool] = None
    
    class Config:
        schema_extra = {
            "example": {
                "resolved": True
            }
        }

class Alert(AlertBase):
    id: str
    timestamp: datetime
    # For station alerts
    stationCode: Optional[str] = None
    stationName: Optional[str] = None
    distance: Optional[float] = None  # in kilometers
    # For theft alerts
    objectId: Optional[str] = None
    objectType: Optional[str] = None
    ownerId: Optional[str] = None
    coachId: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "60d21b4967d0d8992e610c85",
                "type": "station_proximity",
                "trainNumber": "12301",
                "trainName": "Rajdhani Express",
                "timestamp": "2023-05-08T10:30:00Z",
                "resolved": False,
                "stationCode": "NDLS",
                "stationName": "New Delhi Railway Station",
                "distance": 0.85
            }
        }
    
    @classmethod
    def from_mongo(cls, mongo_doc):
        if mongo_doc.get("_id"):
            mongo_doc["id"] = str(mongo_doc.pop("_id"))
        return cls(**mongo_doc)