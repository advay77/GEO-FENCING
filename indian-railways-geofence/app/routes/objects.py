from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson.objectid import ObjectId

from app.models import Object, ObjectCreate, ObjectUpdate, GeoPoint
from app.db.connection import get_database
from app.services.geo_fencing import check_object_theft

router = APIRouter()

@router.get("/", response_model=List[Object])
async def get_objects(db=Depends(get_database)):
    """Get all objects"""
    objects = await db.objects.find().to_list(1000)
    return objects

@router.get("/{object_id}", response_model=Object)
async def get_object(object_id: str, db=Depends(get_database)):
    """Get a specific object by ID"""
    obj = await db.objects.find_one({"id": object_id})
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    return obj

@router.post("/", response_model=Object)
async def create_object(obj: ObjectCreate, db=Depends(get_database)):
    """Create a new object"""
    obj_dict = obj.dict()
    
    # Check if object already exists
    existing = await db.objects.find_one({"id": obj.id})
    if existing:
        raise HTTPException(status_code=400, detail="Object with this ID already exists")
    
    # Verify train and coach exist
    train = await db.trains.find_one({"number": obj.trainNumber})
    if not train:
        raise HTTPException(status_code=404, detail="Train not found")
    
    coach_exists = any(coach["id"] == obj.coachId for coach in train["coaches"])
    if not coach_exists:
        raise HTTPException(status_code=404, detail="Coach not found in train")
    
    result = await db.objects.insert_one(obj_dict)
    created_obj = await db.objects.find_one({"_id": result.inserted_id})
    return created_obj

@router.put("/{object_id}", response_model=Object)
async def update_object(object_id: str, obj_update: ObjectUpdate, db=Depends(get_database)):
    """Update an object"""
    update_data = {k: v for k, v in obj_update.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid update data provided")
    
    # If updating train or coach, verify they exist
    if "trainNumber" in update_data:
        train = await db.trains.find_one({"number": update_data["trainNumber"]})
        if not train:
            raise HTTPException(status_code=404, detail="Train not found")
        
        # If updating coach, verify it exists in the train
        if "coachId" in update_data:
            coach_exists = any(coach["id"] == update_data["coachId"] for coach in train["coaches"])
            if not coach_exists:
                raise HTTPException(status_code=404, detail="Coach not found in train")
    
    result = await db.objects.update_one(
        {"id": object_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Object not found")
    
    updated_obj = await db.objects.find_one({"id": object_id})
    
    # If location was updated, check for theft
    if "location" in update_data:
        await check_object_theft(object_id, db)
    
    return updated_obj

@router.put("/{object_id}/location", response_model=Object)
async def update_object_location(object_id: str, location: GeoPoint, db=Depends(get_database)):
    """Update an object's location"""
    result = await db.objects.update_one(
        {"id": object_id},
        {"$set": {"location": location.dict()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Object not found")
    
    updated_obj = await db.objects.find_one({"id": object_id})
    
    # Check for theft alerts
    await check_object_theft(object_id, db)
    
    return updated_obj

@router.delete("/{object_id}")
async def delete_object(object_id: str, db=Depends(get_database)):
    """Delete an object"""
    result = await db.objects.delete_one({"id": object_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Object not found")
    
    return {"message": "Object deleted successfully"}