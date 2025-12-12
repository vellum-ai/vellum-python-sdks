from typing import Annotated


def get_current_weather(
    date_input: str,
    location: Annotated[str, "The location to get the weather for"],
    units: Annotated[str, "The unit of temperature"] = "fahrenheit",
) -> str:
    return f"The current weather on {date_input} in {location} is sunny with a temperature of 70 degrees {units}."
