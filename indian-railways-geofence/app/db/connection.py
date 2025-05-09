from motor.motor_asyncio import AsyncIOMotorClient
import os
from pymongo import GEOSPHERE

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "railway_geofence")

# Global database connection
client = None
db = None

async def connect_to_mongo():
    """Connect to MongoDB"""
    global client, db
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[MONGODB_DB]
    
    # Create geospatial indexes
    await db.stations.create_index([("location", GEOSPHERE)])
    await db.trains.create_index([("location", GEOSPHERE)])
    await db.objects.create_index([("location", GEOSPHERE)])
    
    # Create other indexes
    await db.trains.create_index("number", unique=True)
    await db.stations.create_index("code", unique=True)
    await db.objects.create_index("id", unique=True)
    await db.users.create_index("email", unique=True)
    await db.users.create_index("phone", unique=True)
    
    print(f"Connected to MongoDB at {MONGODB_URL}, database: {MONGODB_DB}")
    
    return db

async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("MongoDB connection closed")

async def get_database():
    """Get database connection for dependency injection"""
    global db
    if db is None:
        await connect_to_mongo()
    return db