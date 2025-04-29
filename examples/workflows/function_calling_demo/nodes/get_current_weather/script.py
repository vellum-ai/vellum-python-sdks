import googlemaps
import requests

def main(kwargs, gmaps_api_key, openweather_api_key):
    location = kwargs["location"]

    gmaps = googlemaps.Client(key=gmaps_api_key)

    # Geocoding an address
    geocode_result = gmaps.geocode(location)
    print(geocode_result)

    coordinates = geocode_result[0]["geometry"]["location"]
    lat = coordinates["lat"]
    lon = coordinates["lng"]

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid=7b9663b943995d520fdfe643d6838425"
    response = requests.get(url)
    data = response.json()
    
    return data
    