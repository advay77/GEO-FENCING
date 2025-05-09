import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    
    Returns distance in kilometers
    """
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in kilometers
    r = 6371
    
    return c * r

def bearing_between_points(lat1, lon1, lat2, lon2):
    """
    Calculate the bearing between two points on Earth
    
    Returns bearing in degrees (0-360, where 0 is North)
    """
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Calculate bearing
    y = math.sin(lon2 - lon1) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - \
        math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
    
    bearing = math.atan2(y, x)
    
    # Convert from radians to degrees
    bearing = math.degrees(bearing)
    
    # Normalize to 0-360
    bearing = (bearing + 360) % 360
    
    return bearing

def destination_point(lat, lon, bearing, distance):
    """
    Calculate the destination point given a starting point, 
    bearing (in degrees), and distance (in kilometers)
    
    Returns (latitude, longitude) of destination point
    """
    # Convert to radians
    lat = math.radians(lat)
    lon = math.radians(lon)
    bearing = math.radians(bearing)
    
    # Earth's radius in kilometers
    R = 6371
    
    # Angular distance
    d = distance / R
    
    # Calculate destination point
    lat2 = math.asin(math.sin(lat) * math.cos(d) + 
                     math.cos(lat) * math.sin(d) * math.cos(bearing))
    
    lon2 = lon + math.atan2(math.sin(bearing) * math.sin(d) * math.cos(lat),
                           math.cos(d) - math.sin(lat) * math.sin(lat2))
    
    # Convert back to degrees
    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)
    
    return (lat2, lon2)