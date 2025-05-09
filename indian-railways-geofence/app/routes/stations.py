from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson.objectid import ObjectId

from app.models import Station, StationCreate, StationUpdate
from app.db.connection import get_database

router = APIRouter()

@router.get("/", response_model=List[Station])
async def get_stations(db=Depends(get_database)):
    """Get all stations"""
    stations = await db.stations.find().to_list(1000)
    return stations

@router.get("/{station_code}", response_model=Station)
async def get_station(station_code: str, db=Depends(get_database)):
    """Get a specific station by code"""
    station = await db.stations.find_one({"code": station_code})
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return station

@router.post("/", response_model=Station)
async def create_station(station: StationCreate, db=Depends(get_database)):
    """Create a new station"""
    station_dict = station.dict()
    
    # Check if station already exists
    existing = await db.stations.find_one({"code": station.code})
    if existing:
        raise HTTPException(status_code=400, detail="Station with this code already exists")
    
    result = await db.stations.insert_one(station_dict)
    created_station = await db.stations.find_one({"_id": result.inserted_id})
    return created_station

@router.put("/{station_code}", response_model=Station)
async def update_station(station_code: str, station_update: StationUpdate, db=Depends(get_database)):
    """Update a station"""
    update_data = {k: v for k, v in station_update.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid update data provided")
    
    result = await db.stations.update_one(
        {"code": station_code},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Station not found")
    
    updated_station = await db.stations.find_one({"code": station_code})
    return updated_station

@router.delete("/{station_code}")
async def delete_station(station_code: str, db=Depends(get_database)):
    """Delete a station"""
    result = await db.stations.delete_one({"code": station_code})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Station not found")
    
    return {"message": "Station deleted successfully"}