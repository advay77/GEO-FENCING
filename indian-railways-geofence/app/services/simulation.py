import random
import math
from datetime import datetime, timedelta

from app.utils.distance import haversine_distance
from app.services.geo_fencing import check_station_proximity, check_object_theft

async def simulate_train_movement(db, train_number=None, distance_km=None):
    """
    Simulate train movement
    If train_number is provided, only move that train
    If distance_km is provided, move train by that distance
    """
    query = {}
    if train_number:
        query["number"] = train_number
    
    trains = await db.trains.find(query).to_list(1000)
    updated_trains = []
    
    for train in trains:
        # If specific distance provided, calculate speed to move that distance
        if distance_km:
            # Convert distance from km to degrees (approximate)
            distance_in_degrees = distance_km / 111
            
            # Calculate new coordinates based on direction
            direction_radians = (train["direction"] * math.pi) / 180
            new_lon = train["location"]["coordinates"][0] + distance_in_degrees * math.cos(direction_radians)
            new_lat = train["location"]["coordinates"][1] + distance_in_degrees * math.sin(direction_radians)
        else:
            # Calculate new position based on speed and direction
            # Speed is in km/h, convert to degrees per interval (5 seconds)
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
    
    return updated_trains

async def simulate_object_theft(db, object_id, distance_km=0.1):
    """Simulate object theft by moving it away from its train"""
    obj = await db.objects.find_one({"id": object_id})
    if not obj:
        return None
    
    # Get current coordinates
    current_coords = obj["location"]["coordinates"]
    
    # Move object by specified distance in a random direction
    angle = random.random() * 2 * math.pi
    # Convert distance from km to degrees (approximate)
    distance_in_degrees = distance_km / 111
    
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
        "object": updated_obj,
        "requested_distance_km": distance_km,
        "actual_distance_km": actual_distance
    }

async def simulate_full_journey(db, train_number, destination_station, duration_minutes=30, interval_seconds=30):
    """Simulate a full journey from current location to destination station"""
    train = await db.trains.find_one({"number": train_number})
    if not train:
        return None
    
    destination = await db.stations.find_one({"code": destination_station})
    if not destination:
        return None
    
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
        "train": train,
        "destination": destination,
        "distance_km": total_distance,
        "duration_minutes": duration_minutes,
        "speed_kmh": required_speed,
        "direction_degrees": bearing,
        "updates_count": duration_minutes * 60 // interval_seconds
    }