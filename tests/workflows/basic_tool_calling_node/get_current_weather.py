import math


def get_current_weather(location: str, unit: str) -> str:
    """
    Get the current weather in a given location.
    """
    return f"The current weather in {location} is sunny with a temperature of {get_temperature(70.1)} degrees {unit}."


def get_temperature(temperature: float) -> int:
    """
    Get the temperature in a given location.
    """
    return math.floor(temperature)
