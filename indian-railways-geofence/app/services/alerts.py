from datetime import datetime, timedelta

async def get_active_alerts(db, alert_type=None, train_number=None):
    """Get all active (unresolved) alerts with optional filters"""
    query = {"resolved": False}
    
    if alert_type:
        query["type"] = alert_type
    
    if train_number:
        query["trainNumber"] = train_number
    
    return await db.alerts.find(query).sort("timestamp", -1).to_list(1000)

async def get_alerts_by_user(db, user_id):
    """Get alerts relevant to a specific user"""
    # Get user information
    user = await db.users.find_one({"_id": user_id})
    if not user:
        return []
    
    # Get alerts for user's current train
    train_alerts = []
    if user.get("currentTrain"):
        train_alerts = await db.alerts.find({
            "trainNumber": user["currentTrain"],
            "resolved": False
        }).to_list(1000)
    
    # Get alerts for user's registered objects
    object_alerts = []
    if user.get("registeredObjects"):
        object_alerts = await db.alerts.find({
            "objectId": {"$in": user["registeredObjects"]},
            "type": "theft",
            "resolved": False
        }).to_list(1000)
    
    # Combine and sort alerts
    all_alerts = train_alerts + object_alerts
    all_alerts.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return all_alerts

async def get_alert_stats(db, days=7):
    """Get alert statistics for the specified number of days"""
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
    
    # Get alerts by train
    train_stats = []
    trains = await db.trains.find().to_list(1000)
    
    for train in trains:
        count = await db.alerts.count_documents({
            "trainNumber": train["number"],
            "timestamp": {"$gte": since_date}
        })
        
        if count > 0:
            train_stats.append({
                "trainNumber": train["number"],
                "trainName": train["name"],
                "alertCount": count
            })
    
    # Sort trains by alert count
    train_stats.sort(key=lambda x: x["alertCount"], reverse=True)
    
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
        "by_train": train_stats,
        "period_days": days
    }