from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import datetime, timedelta

from app.models import Alert, AlertCreate, AlertUpdate
from app.db.connection import get_database

router = APIRouter()

@router.get("/", response_model=List[Alert])
async def get_alerts(
    alert_type: Optional[str] = Query(None, description="Filter by alert type: 'station_proximity' or 'theft'"),
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    train_number: Optional[str] = Query(None, description="Filter by train number"),
    object_id: Optional[str] = Query(None, description="Filter by object ID"),
    station_code: Optional[str] = Query(None, description="Filter by station code"),
    since: Optional[datetime] = Query(None, description="Filter alerts since timestamp"),
    db=Depends(get_database)
):
    """Get alerts with optional filters"""
    query = {}
    
    if alert_type:
        query["type"] = alert_type
    
    if resolved is not None:
        query["resolved"] = resolved
    
    if train_number:
        query["trainNumber"] = train_number
    
    if object_id:
        query["objectId"] = object_id
    
    if station_code:
        query["stationCode"] = station_code
    
    if since:
        query["timestamp"] = {"$gte": since}
    
    alerts = await db.alerts.find(query).sort("timestamp", -1).to_list(1000)
    
    return [Alert(id=str(alert["_id"]), **{k: v for k, v in alert.items() if k != "_id"}) for alert in alerts]

@router.get("/{alert_id}", response_model=Alert)
async def get_alert(alert_id: str, db=Depends(get_database)):
    """Get a specific alert by ID"""
    try:
        alert = await db.alerts.find_one({"_id": ObjectId(alert_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid alert ID format")
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return Alert(id=str(alert["_id"]), **{k: v for k, v in alert.items() if k != "_id"})

@router.post("/", response_model=Alert)
async def create_alert(alert: AlertCreate, db=Depends(get_database)):
    """Create a new alert (usually done by the system)"""
    alert_dict = alert.dict()
    
    # Validate alert data based on type
    if alert.type == "station_proximity":
        if not all([alert.stationCode, alert.stationName, alert.distance is not None]):
            raise HTTPException(status_code=400, detail="Station proximity alerts require stationCode, stationName, and distance")
    elif alert.type == "theft":
        if not all([alert.objectId, alert.objectType, alert.ownerId, alert.coachId]):
            raise HTTPException(status_code=400, detail="Theft alerts require objectId, objectType, ownerId, and coachId")
    
    result = await db.alerts.insert_one(alert_dict)
    created_alert = await db.alerts.find_one({"_id": result.inserted_id})
    
    return Alert(id=str(created_alert["_id"]), **{k: v for k, v in created_alert.items() if k != "_id"})

@router.put("/{alert_id}/resolve")
async def resolve_alert(alert_id: str, db=Depends(get_database)):
    """Resolve an alert"""
    try:
        object_id = ObjectId(alert_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid alert ID format")
    
    result = await db.alerts.update_one(
        {"_id": object_id},
        {"$set": {"resolved": True}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert resolved successfully"}

@router.get("/stats/summary")
async def get_alert_stats(
    days: int = Query(7, description="Number of days to include in stats"),
    db=Depends(get_database)
):
    """Get alert statistics summary"""
    since_date = datetime.now() - timedelta(days=days)
    
    # Get counts by type
    station_alerts = await db.alerts.count_documents({
        "type": "station_proximity",
        "timestamp": {"$gte": since_date}
    })
    
    theft_alerts = await db.alerts.count_documents({
        "type": "theft",
        "timestamp": {"$gte": since_date}
    })
    
    # Get counts by resolved status
    resolved = await db.alerts.count_documents({
        "resolved": True,
        "timestamp": {"$gte": since_date}
    })
    
    unresolved = await db.alerts.count_documents({
        "resolved": False,
        "timestamp": {"$gte": since_date}
    })
    
    return {
        "total": station_alerts + theft_alerts,
        "by_type": {
            "station_proximity": station_alerts,
            "theft": theft_alerts
        },
        "by_status": {
            "resolved": resolved,
            "unresolved": unresolved
        },
        "period_days": days
    }