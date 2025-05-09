from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson.objectid import ObjectId

from app.models import User, UserCreate, UserUpdate
from app.db.connection import get_database

router = APIRouter()

@router.get("/", response_model=List[User])
async def get_users(db=Depends(get_database)):
    """Get all users"""
    users = await db.users.find().to_list(1000)
    return [User(id=str(user["_id"]), **{k: v for k, v in user.items() if k != "_id"}) for user in users]

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, db=Depends(get_database)):
    """Get a specific user by ID"""
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(id=str(user["_id"]), **{k: v for k, v in user.items() if k != "_id"})

@router.post("/", response_model=User)
async def create_user(user: UserCreate, db=Depends(get_database)):
    """Create a new user"""
    user_dict = user.dict()
    
    # Check if user with same email or phone exists
    existing = await db.users.find_one({"$or": [{"email": user.email}, {"phone": user.phone}]})
    if existing:
        raise HTTPException(status_code=400, detail="User with this email or phone already exists")
    
    # Verify train and coach if provided
    if user.currentTrain:
        train = await db.trains.find_one({"number": user.currentTrain})
        if not train:
            raise HTTPException(status_code=404, detail="Train not found")
        
        if user.currentCoach:
            coach_exists = any(coach["id"] == user.currentCoach for coach in train["coaches"])
            if not coach_exists:
                raise HTTPException(status_code=404, detail="Coach not found in train")
    
    result = await db.users.insert_one(user_dict)
    created_user = await db.users.find_one({"_id": result.inserted_id})
    
    return User(id=str(created_user["_id"]), **{k: v for k, v in created_user.items() if k != "_id"})

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, user_update: UserUpdate, db=Depends(get_database)):
    """Update a user"""
    try:
        object_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid update data provided")
    
    # If updating 
        raise HTTPException(status_code=400, detail="No valid update data provided")
    
    # If updating email or phone, check if they're already in use
    if "email" in update_data or "phone" in update_data:
        query = {"_id": {"$ne": object_id}}
        
        if "email" in update_data:
            query["email"] = update_data["email"]
        
        if "phone" in update_data:
            query["phone"] = update_data["phone"]
        
        existing = await db.users.find_one(query)
        if existing:
            raise HTTPException(status_code=400, detail="Email or phone already in use")
    
    # Verify train and coach if provided
    if "currentTrain" in update_data:
        train = await db.trains.find_one({"number": update_data["currentTrain"]})
        if not train:
            raise HTTPException(status_code=404, detail="Train not found")
        
        if "currentCoach" in update_data:
            coach_exists = any(coach["id"] == update_data["currentCoach"] for coach in train["coaches"])
            if not coach_exists:
                raise HTTPException(status_code=404, detail="Coach not found in train")
    
    result = await db.users.update_one(
        {"_id": object_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = await db.users.find_one({"_id": object_id})
    
    return User(id=str(updated_user["_id"]), **{k: v for k, v in updated_user.items() if k != "_id"})

@router.delete("/{user_id}")
async def delete_user(user_id: str, db=Depends(get_database)):
    """Delete a user"""
    try:
        object_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    result = await db.users.delete_one({"_id": object_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}

@router.get("/{user_id}/objects", response_model=List[object])
async def get_user_objects(user_id: str, db=Depends(get_database)):
    """Get all objects registered to a user"""
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    objects = await db.objects.find({"id": {"$in": user.get("registeredObjects", [])}}).to_list(1000)
    
    return objects