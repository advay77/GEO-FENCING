from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

class UserBase(BaseModel):
    name: str
    phone: str
    email: EmailStr

class UserCreate(UserBase):
    currentTrain: Optional[str] = None
    currentCoach: Optional[str] = None
    registeredObjects: List[str] = []
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Rahul Sharma",
                "phone": "+919876543210",
                "email": "rahul@example.com",
                "currentTrain": "12301",
                "currentCoach": "A1",
                "registeredObjects": ["OBJ001", "OBJ002"]
            }
        }

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    currentTrain: Optional[str] = None
    currentCoach: Optional[str] = None
    registeredObjects: Optional[List[str]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "currentTrain": "12301",
                "currentCoach": "B1"
            }
        }

class User(UserBase):
    id: str
    currentTrain: Optional[str] = None
    currentCoach: Optional[str] = None
    registeredObjects: List[str] = []
    
    class Config:
        schema_extra = {
            "example": {
                "id": "60d21b4967d0d8992e610c85",
                "name": "Rahul Sharma",
                "phone": "+919876543210",
                "email": "rahul@example.com",
                "currentTrain": "12301",
                "currentCoach": "A1",
                "registeredObjects": ["OBJ001", "OBJ002"]
            }
        }
    
    @classmethod
    def from_mongo(cls, mongo_doc):
        if mongo_doc.get("_id"):
            mongo_doc["id"] = str(mongo_doc.pop("_id"))
        return cls(**mongo_doc)