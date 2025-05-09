import sys
import os

# Add the parent directory of 'app' to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from app.db.connection import connect_to_mongo, close_mongo_connection
from app.routes import trains, stations, objects, users, alerts, simulation
from app.db.seed import seed_initial_data

# Initialize FastAPI app
app = FastAPI(
    title="Indian Railways Geo-Fencing API",
    description="API for real-time geo-fencing alerts in Indian Railways",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trains.router, prefix="/trains", tags=["Trains"])
app.include_router(stations.router, prefix="/stations", tags=["Stations"])
app.include_router(objects.router, prefix="/objects", tags=["Objects"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
app.include_router(simulation.router, prefix="/simulate", tags=["Simulation"])

# Startup and shutdown events
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()
    await seed_initial_data()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)