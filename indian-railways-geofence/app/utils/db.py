from bson import ObjectId
from datetime import datetime

def format_mongo_doc(doc):
    """Format MongoDB document for API response"""
    if doc is None:
        return None
    
    # Convert ObjectId to string
    if "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    
    # Format datetime objects
    for key, value in doc.items():
        if isinstance(value, datetime):
            doc[key] = value.isoformat()
        elif isinstance(value, ObjectId):
            doc[key] = str(value)
    
    return doc

def prepare_mongo_query(query_params):
    """Prepare MongoDB query from API query parameters"""
    mongo_query = {}
    
    for key, value in query_params.items():
        if value is None:
            continue
        
        # Handle special query parameters
        if key.endswith("_gt"):
            field = key[:-3]
            mongo_query[field] = mongo_query.get(field, {})
            mongo_query[field]["$gt"] = value
        elif key.endswith("_gte"):
            field = key[:-4]
            mongo_query[field] = mongo_query.get(field, {})
            mongo_query[field]["$gte"] = value
        elif key.endswith("_lt"):
            field = key[:-3]
            mongo_query[field] = mongo_query.get(field, {})
            mongo_query[field]["$lt"] = value
        elif key.endswith("_lte"):
            field = key[:-4]
            mongo_query[field] = mongo_query.get(field, {})
            mongo_query[field]["$lte"] = value
        elif key.endswith("_ne"):
            field = key[:-3]
            mongo_query[field] = mongo_query.get(field, {})
            mongo_query[field]["$ne"] = value
        elif key.endswith("_in"):
            field = key[:-3]
            if isinstance(value, list):
                mongo_query[field] = {"$in": value}
        elif key.endswith("_nin"):
            field = key[:-4]
            if isinstance(value, list):
                mongo_query[field] = {"$nin": value}
        else:
            mongo_query[key] = value
    
    return mongo_query