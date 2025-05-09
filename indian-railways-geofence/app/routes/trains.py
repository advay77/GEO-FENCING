from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson.objectid import ObjectId

from app.models import Train, TrainCreate, TrainUpdate, GeoPoint
from app.db.connection import get_database
from app.services.geo_fencing import check_station_proximity

router = APIRouter()

@router.get("/", response_model=List[Train])
async def get_trains(db=Depends(get_database)):
    """Get all trains"""
    trains = await db.trains.find().to_list(1000)
    return trains

@router.get("/{train_number}", response_model=Train)
async def get_train(train_number: str, db=Depends(get_database)):
    """Get a specific train by number"""
    train = await db.trains.find_one({"number": train_number})
    if not train:
        raise HTTPException(status_code=404, detail="Train not found")
    return train

@router.post("/", response_model=Train)
async def create_train(train: TrainCreate, db=Depends(get_database)):
    """Create a new train"""
    train_dict = train.dict()
    
    # Check if train already exists
    existing = await db.trains.find_one({"number": train.number})
    if existing:
        raise HTTPException(status_code=400, detail="Train with this number already exists")
    
    result = await db.trains.insert_one(train_dict)
    created_train = await db.trains.find_one({"_id": result.inserted_id})
    return created_train

@router.put("/{train_number}", response_model=Train)
async def update_train(train_number: str, train_update: TrainUpdate, db=Depends(get_database)):
    """Update a train"""
    update_data = {k: v for k, v in train_update.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid update data provided")
    
    result = await db.trains.update_one(
        {"number": train_number},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Train not found")
    
    updated_train = await db.trains.find_one({"number": train_number})
    return updated_train

@router.put("/{train_number}/location", response_model=Train)
async def update_train_location(train_number: str, location: GeoPoint, db=Depends(get_database)):
    """Update a train's location"""
    result = await db.trains.update_one(
        {"number": train_number},
        {"$set": {"location": location.dict()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Train not found")
    
    # Update objects that should move with the train
    await db.objects.update_many(
        {"trainNumber": train_number},
        {"$set": {"location": location.dict()}}
    )
    
    updated_train = await db.trains.find_one({"number": train_number})
    
    # Check for station proximity
    await check_station_proximity(train_number, db)
    
    return updated_train

@router.delete("/{train_number}")
async def delete_train(train_number: str, db=Depends(get_database)):
    """Delete a train"""
    result = await db.trains.delete_one({"number": train_number})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Train not found")
    
    return {"message": "Train deleted successfully"}