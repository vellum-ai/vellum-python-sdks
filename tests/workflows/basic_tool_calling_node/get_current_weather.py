import math


def get_current_weather(location: str, unit: str) -> str:
    """
    Get the current weather in a given location.
    """
    return f"The current weather in {location} is sunny with a temperature of {math.floor(70.1)} degrees {unit}."
