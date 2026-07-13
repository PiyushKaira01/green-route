from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def get_coordinates(location_name):
    """
    Takes a string like 'India Gate, New Delhi' and returns (Latitude, Longitude).
    """
    
    # We will use the exact input so places like "Taj Mahal, Agra" actually work!
    search_query = location_name

    print(f"🌍 Geocoding: Looking up '{search_query}'...")
    
    # Nominatim requires a unique user_agent for their free API
    geolocator = Nominatim(user_agent="green_route_btech_project")
    
    try:
        # Ask the API for the location
        location = geolocator.geocode(search_query, timeout=10)
        
        if location:
            print(f"📍 Found: {location.address} -> ({location.latitude}, {location.longitude})")
            return location.latitude, location.longitude
        else:
            print(f"❌ Error: OpenStreetMap couldn't find '{search_query}'. Try being more specific!")
            return None, None
            
    except GeocoderTimedOut:
        print("⏳ Error: Geocoding service timed out.")
        return None, None