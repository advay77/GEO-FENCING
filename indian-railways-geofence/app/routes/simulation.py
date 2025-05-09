from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import random
import math
from datetime import datetime

from app.models import Train, Object
from app.db.connection import get_database
from app.services.geo_fencing import check_station_proximity, check_object_theft
from app.utils.distance import haversine_distance

router = APIRouter()

@router.post("/train-movement")
async def simulate_train_movement(db=Depends(get_database)):
    """Simulate train movement for testing purposes"""
    trains = await db.trains.find().to_list(1000)
    
    updated_trains = []
    
    for train in trains:
        # Calculate new position based on speed and direction
        # Speed is in km/h, convert to degrees per interval
        # Approximate conversion: 1 degree ≈ 111 km at the equator
        speed_in_degrees = (train["speed"] / 3600) * 5 / 111
        
        # Calculate new coordinates based on direction
        direction_radians = (train["direction"] * math.pi) / 180
        new_lon = train["location"]["coordinates"][0] + speed_in_degrees * math.cos(direction_radians)
        new_lat = train["location"]["coordinates"][1] + speed_in_degrees * math.sin(direction_radians)
        
        # Update train location
        await db.trains.update_one(
            {"number": train["number"]},
            {
                "$set": {
                    "location.coordinates": [new_lon, new_lat],
                    # Randomly change direction slightly to simulate realistic movement
                    "direction": (train["direction"] + (10 * (0.5 - random.random()))) % 360
                }
            }
        )
        
        # Update objects that should move with the train
        await db.objects.update_many(
            {"trainNumber": train["number"]},
            {"$set": {"location.coordinates": [new_lon, new_lat]}}
        )
        
        # Check for station proximity
        await check_station_proximity(train["number"], db)
        
        updated_train = await db.trains.find_one({"number": train["number"]})
        updated_trains.append(updated_train)
    
    return {
        "message": "Train movement simulated successfully",
        "updated_trains": len(updated_trains)
    }

@router.post("/object-theft/{object_id}")
async def simulate_object_theft(
    object_id: str, 
    distance: float = Query(0.1, description="Distance to move object in km"),
    db=Depends(get_database)
):
    """Simulate object theft by moving it away from its train"""
    obj = await db.objects.find_one({"id": object_id})
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    
    # Get current coordinates
    current_coords = obj["location"]["coordinates"]
    
    # Move object by specified distance in a random direction
    angle = random.random() * 2 * math.pi
    # Convert distance from km to degrees (approximate)
    distance_in_degrees = distance / 111
    
    new_lon = current_coords[0] + distance_in_degrees * math.cos(angle)
    new_lat = current_coords[1] + distance_in_degrees * math.sin(angle)
    
    # Update object location
    await db.objects.update_one(
        {"id": object_id},
        {"$set": {"location.coordinates": [new_lon, new_lat]}}
    )
    
    # Check for theft alert
    await check_object_theft(object_id, db)
    
    updated_obj = await db.objects.find_one({"id": object_id})
    
    # Get train location to calculate actual distance
    train = await db.trains.find_one({"number": obj["trainNumber"]})
    if train:
        train_coords = train["location"]["coordinates"]
        actual_distance = haversine_distance(
            updated_obj["location"]["coordinates"][1], updated_obj["location"]["coordinates"][0],
            train_coords[1], train_coords[0]
        )
    else:
        actual_distance = None
    
    return {
        "message": f"Object moved away from train",
        "requested_distance_km": distance,
        "actual_distance_km": actual_distance,
        "new_coordinates": updated_obj["location"]["coordinates"]
    }

@router.post("/full-journey/{train_number}")
async def simulate_full_journey(
    train_number: str,
    destination_station: str,
    duration_minutes: int = Query(30, description="Duration of journey simulation in minutes"),
    interval_seconds: int = Query(30, description="Interval between updates in seconds"),
    db=Depends(get_database)
):
    """Simulate a full journey from current location to destination station"""
    train = await db.trains.find_one({"number": train_number})
    if not train:
        raise HTTPException(status_code=404, detail="Train not found")
    
    destination = await db.stations.find_one({"code": destination_station})
    if not destination:
        raise HTTPException(status_code=404, detail="Destination station not found")
    
    # Calculate total distance and bearing to destination
    start_coords = train["location"]["coordinates"]
    dest_coords = destination["location"]["coordinates"]
    
    total_distance = haversine_distance(
        start_coords[1], start_coords[0],
        dest_coords[1], dest_coords[0]
    )
    
    # Calculate required speed to reach destination in given time
    required_speed = (total_distance / duration_minutes) * 60  # km/h
    
    # Calculate bearing to destination
    y = math.sin(dest_coords[0] - start_coords[0]) * math.cos(dest_coords[1])
    x = math.cos(start_coords[1]) * math.sin(dest_coords[1]) - \
        math.sin(start_coords[1]) * math.cos(dest_coords[1]) * math.cos(dest_coords[0] - start_coords[0])
    bearing = (math.atan2(y, x) * 180 / math.pi + 360) % 360
    
    # Update train with new speed and direction
    await db.trains.update_one(
        {"number": train_number},
        {"$set": {"speed": required_speed, "direction": bearing}}
    )
    
    return {
        "message": f"Journey simulation started",
        "train": train_number,
        "destination": destination["name"],
        "distance_km": total_distance,
        "duration_minutes": duration_minutes,
        "speed_kmh": required_speed,
        "direction_degrees": bearing,
        "updates_count": duration_minutes * 60 // interval_seconds
    }

@router.post("/random-events")
async def simulate_random_events(
    theft_probability: float = Query(0.2, description="Probability of theft event (0-1)"),
    count: int = Query(1, description="Number of random events to generate"),
    db=Depends(get_database)
):
    """Simulate random events in the system (thefts, train movements, etc.)"""
    events = []
    
    for _ in range(count):
        event_type = random.random()
        
        if event_type < theft_probability:
            # Simulate theft
            objects = await db.objects.find().to_list(1000)
            if objects:
                random_object = random.choice(objects)
                distance = 0.05 + random.random() * 0.2  # 50m to 250m
                
                # Move object away from train
                current_coords = random_object["location"]["coordinates"]
                angle = random.random() * 2 * math.pi
                distance_in_degrees = distance / 111
                
                new_lon = current_coords[0] + distance_in_degrees * math.cos(angle)
                new_lat = current_coords[1] + distance_in_degrees * math.sin(angle)
                
                await db.objects.update_one(
                    {"id": random_object["id"]},
                    {"$set": {"location.coordinates": [new_lon, new_lat]}}
                )
                
                await check_object_theft(random_object["id"], db)
                
                events.append({
                    "type": "theft_simulation",
                    "object_id": random_object["id"],
                    "distance_km": distance
                })
        else:
            # Simulate train movement
            trains = await db.trains.find().to_list(1000)
            if trains:
                random_train = random.choice(trains)
                
                # Calculate new position
                speed_in_degrees = (random_train["speed"] / 3600) * 5 / 111
                direction_radians = (random_train["direction"] * math.pi) / 180
                new_lon = random_train["location"]["coordinates"][0] + speed_in_degrees * math.cos(direction_radians)
                new_lat = random_train["location"]["coordinates"][1] + speed_in_degrees * math.sin(direction_radians)
                
                # Update train location
                await db.trains.update_one(
                    {"number": random_train["number"]},
                    {
                        "$set": {
                            "location.coordinates": [new_lon, new_lat],
                            "direction": (random_train["direction"] + (10 * (0.5 - random.random()))) % 360
                        }
                    }
                )
                
                # Update objects that should move with the train
                await db.objects.update_many(
                    {"trainNumber": random_train["number"]},
                    {"$set": {"location.coordinates": [new_lon, new_lat]}}
                )
                
                await check_station_proximity(random_train["number"], db)
                
                events.append({
                    "type": "train_movement",
                    "train_number": random_train["number"],
                    "new_coordinates": [new_lon, new_lat]
                })
    
    return {
        "message": f"Generated {len(events)} random events",
        "events": events
    }