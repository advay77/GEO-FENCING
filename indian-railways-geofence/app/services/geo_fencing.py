from datetime import datetime
import os

from app.utils.distance import haversine_distance
from app.models import AlertCreate

# Get geo-fencing settings from environment variables
STATION_PROXIMITY_RADIUS = float(os.getenv("STATION_PROXIMITY_RADIUS", 1.0))  # km
DEFAULT_COACH_GEOFENCE_RADIUS = float(os.getenv("DEFAULT_COACH_GEOFENCE_RADIUS", 0.05))  # km

async def check_station_proximity(train_number, db):
    """Check if a train is entering a station's proximity radius"""
    train = await db.trains.find_one({"number": train_number})
    if not train:
        return
    
    stations = await db.stations.find().to_list(1000)
    
    for station in stations:
        train_coords = train["location"]["coordinates"]
        station_coords = station["location"]["coordinates"]
        
        # Calculate distance using Haversine formula
        distance = haversine_distance(
            train_coords[1], train_coords[0],  # lat, lon
            station_coords[1], station_coords[0]  # lat, lon
        )
        
        # Check if train is within proximity radius of station
        if distance <= STATION_PROXIMITY_RADIUS:
            # Check if we've already alerted for this train-station pair
            existing_alert = await db.alerts.find_one({
                "type": "station_proximity",
                "trainNumber": train["number"],
                "stationCode": station["code"],
                "resolved": False
            })
            
            if not existing_alert:
                # Create new alert
                alert = AlertCreate(
                    type="station_proximity",
                    trainNumber=train["number"],
                    trainName=train["name"],
                    stationCode=station["code"],
                    stationName=station["name"],
                    distance=distance,
                    timestamp=datetime.now(),
                    resolved=False
                )
                
                await db.alerts.insert_one(alert.dict())
                print(f"ALERT: Train {train['name']} is entering {station['name']} ({distance:.2f} km away)")
                
                # In a real system, we would send push notifications to passengers here
        else:
            # If train is outside the radius, resolve any existing alerts
            await db.alerts.update_many(
                {
                    "type": "station_proximity",
                    "trainNumber": train["number"],
                    "stationCode": station["code"],
                    "resolved": False
                },
                {
                    "$set": {"resolved": True}
                }
            )

async def check_object_theft(object_id, db):
    """Check if an object has moved outside its train's geo-fence"""
    obj = await db.objects.find_one({"id": object_id})
    if not obj:
        return
    
    # Get the train information
    train = await db.trains.find_one({"number": obj["trainNumber"]})
    if not train:
        return
    
    # Find the coach
    coach = next((c for c in train["coaches"] if c["id"] == obj["coachId"]), None)
    if not coach:
        return
    
    # Calculate distance between object and train
    object_coords = obj["location"]["coordinates"]
    train_coords = train["location"]["coordinates"]
    
    distance = haversine_distance(
        object_coords[1], object_coords[0],
        train_coords[1], train_coords[0]
    )
    
    # Get geofence radius (default if not specified)
    geofence_radius = coach.get("geofenceRadius", DEFAULT_COACH_GEOFENCE_RADIUS)
    
    # Check if object is outside the geo-fence
    if distance > geofence_radius:
        # Check if we've already alerted for this object
        existing_alert = await db.alerts.find_one({
            "type": "theft",
            "objectId": obj["id"],
            "resolved": False
        })
        
        if not existing_alert:
            # Get owner information
            owner = await db.users.find_one({"name": obj["ownerId"]})
            
            # Create new theft alert
            alert = AlertCreate(
                type="theft",
                trainNumber=train["number"],
                trainName=train["name"],
                objectId=obj["id"],
                objectType=obj["type"],
                ownerId=obj["ownerId"],
                coachId=obj["coachId"],
                distance=distance,
                timestamp=datetime.now(),
                resolved=False
            )
            
            await db.alerts.insert_one(alert.dict())
            print(f"THEFT ALERT: Object {obj['id']} ({obj['type']}) has moved {distance*1000:.2f} meters outside train {train['name']}, coach {obj['coachId']}")
            
            # In a real system, we would send push notifications to the owner here
    else:
        # If object is back inside the geo-fence, resolve any existing alerts
        await db.alerts.update_many(
            {
                "type": "theft",
                "objectId": obj["id"],
                "resolved": False
            },
            {
                "$set": {"resolved": True}
            }
        )