from app.db.connection import get_database

async def seed_initial_data():
    """Seed initial data if collections are empty"""
    db = await get_database()
    
    # Check if stations collection is empty
    if await db.stations.count_documents({}) == 0:
        # Seed stations (using real Indian railway stations)
        stations = [
            {
                "name": "New Delhi Railway Station",
                "code": "NDLS",
                "location": {
                    "type": "Point",
                    "coordinates": [77.2207, 28.6425]  # [longitude, latitude]
                }
            },
            {
                "name": "Mumbai Central",
                "code": "BCT",
                "location": {
                    "type": "Point",
                    "coordinates": [72.8213, 18.9712]
                }
            },
            {
                "name": "Chennai Central",
                "code": "MAS",
                "location": {
                    "type": "Point",
                    "coordinates": [80.2707, 13.0827]
                }
            },
            {
                "name": "Howrah Junction",
                "code": "HWH",
                "location": {
                    "type": "Point",
                    "coordinates": [88.3426, 22.5839]
                }
            },
            {
                "name": "Bengaluru City Junction",
                "code": "SBC",
                "location": {
                    "type": "Point",
                    "coordinates": [77.5738, 12.9784]
                }
            },
            {
                "name": "Ahmedabad Junction",
                "code": "ADI",
                "location": {
                    "type": "Point",
                    "coordinates": [72.5714, 23.0225]
                }
            },
            {
                "name": "Pune Junction",
                "code": "PUNE",
                "location": {
                    "type": "Point",
                    "coordinates": [73.8744, 18.5284]
                }
            },
            {
                "name": "Jaipur Junction",
                "code": "JP",
                "location": {
                    "type": "Point",
                    "coordinates": [75.7873, 26.9124]
                }
            }
        ]
        await db.stations.insert_many(stations)
        print("Stations data seeded")
    
    # Check if trains collection is empty
    if await db.trains.count_documents({}) == 0:
        # Seed trains
        trains = [
            {
                "name": "Rajdhani Express",
                "number": "12301",
                "location": {
                    "type": "Point",
                    "coordinates": [77.1000, 28.5500]  # Starting near Delhi
                },
                "speed": 80,  # km/h
                "direction": 0,  # degrees, 0 = East, 90 = North, etc.
                "coaches": [
                    {"id": "A1", "geofenceRadius": 0.05},  # 50 meters
                    {"id": "A2", "geofenceRadius": 0.05},
                    {"id": "B1", "geofenceRadius": 0.05}
                ]
            },
            {
                "name": "Shatabdi Express",
                "number": "12002",
                "location": {
                    "type": "Point",
                    "coordinates": [77.3000, 28.6000]  # Starting near Delhi
                },
                "speed": 90,
                "direction": 180,  # Heading south
                "coaches": [
                    {"id": "C1", "geofenceRadius": 0.05},
                    {"id": "C2", "geofenceRadius": 0.05},
                    {"id": "D1", "geofenceRadius": 0.05}
                ]
            },
            {
                "name": "Duronto Express",
                "number": "12213",
                "location": {
                    "type": "Point",
                    "coordinates": [72.8500, 19.0500]  # Starting near Mumbai
                },
                "speed": 85,
                "direction": 45,  # Heading northeast
                "coaches": [
                    {"id": "A1", "geofenceRadius": 0.05},
                    {"id": "A2", "geofenceRadius": 0.05},
                    {"id": "B1", "geofenceRadius": 0.05},
                    {"id": "S1", "geofenceRadius": 0.05}
                ]
            },
            {
                "name": "Garib Rath",
                "number": "12909",
                "location": {
                    "type": "Point",
                    "coordinates": [80.2500, 13.0500]  # Starting near Chennai
                },
                "speed": 75,
                "direction": 270,  # Heading west
                "coaches": [
                    {"id": "G1", "geofenceRadius": 0.05},
                    {"id": "G2", "geofenceRadius": 0.05},
                    {"id": "G3", "geofenceRadius": 0.05}
                ]
            }
        ]
        await db.trains.insert_many(trains)
        print("Trains data seeded")
    
    # Check if users collection is empty
    if await db.users.count_documents({}) == 0:
        # Seed users
        users = [
            {
                "name": "Rahul Sharma",
                "phone": "+919876543210",
                "email": "rahul@example.com",
                "currentTrain": "12301",
                "currentCoach": "A1",
                "registeredObjects": ["OBJ001", "OBJ002"]
            },
            {
                "name": "Priya Patel",
                "phone": "+919876543211",
                "email": "priya@example.com",
                "currentTrain": "12002",
                "currentCoach": "C2",
                "registeredObjects": ["OBJ003"]
            },
            {
                "name": "Amit Kumar",
                "phone": "+919876543212",
                "email": "amit@example.com",
                "currentTrain": "12213",
                "currentCoach": "A2",
                "registeredObjects": ["OBJ004", "OBJ005"]
            },
            {
                "name": "Sneha Gupta",
                "phone": "+919876543213",
                "email": "sneha@example.com",
                "currentTrain": "12909",
                "currentCoach": "G1",
                "registeredObjects": ["OBJ006"]
            }
        ]
        await db.users.insert_many(users)
        print("Users data seeded")
    
    # Check if objects collection is empty
    if await db.objects.count_documents({}) == 0:
        # Seed tracked objects
        objects = [
            {
                "id": "OBJ001",
                "type": "Luggage",
                "ownerId": "Rahul Sharma",
                "trainNumber": "12301",
                "coachId": "A1",
                "location": {
                    "type": "Point",
                    "coordinates": [77.1000, 28.5500]  # Same as train initially
                }
            },
            {
                "id": "OBJ002",
                "type": "Laptop Bag",
                "ownerId": "Rahul Sharma",
                "trainNumber": "12301",
                "coachId": "A1",
                "location": {
                    "type": "Point",
                    "coordinates": [77.1000, 28.5500]
                }
            },
            {
                "id": "OBJ003",
                "type": "Suitcase",
                "ownerId": "Priya Patel",
                "trainNumber": "12002",
                "coachId": "C2",
                "location": {
                    "type": "Point",
                    "coordinates": [77.3000, 28.6000]
                }
            },
            {
                "id": "OBJ004",
                "type": "Backpack",
                "ownerId": "Amit Kumar",
                "trainNumber": "12213",
                "coachId": "A2",
                "location": {
                    "type": "Point",
                    "coordinates": [72.8500, 19.0500]
                }
            },
            {
                "id": "OBJ005",
                "type": "Camera Bag",
                "ownerId": "Amit Kumar",
                "trainNumber": "12213",
                "coachId": "A2",
                "location": {
                    "type": "Point",
                    "coordinates": [72.8500, 19.0500]
                }
            },
            {
                "id": "OBJ006",
                "type": "Travel Bag",
                "ownerId": "Sneha Gupta",
                "trainNumber": "12909",
                "coachId": "G1",
                "location": {
                    "type": "Point",
                    "coordinates": [80.2500, 13.0500]
                }
            }
        ]
        await db.objects.insert_many(objects)
        print("Objects data seeded")