import random
import time


class MyCustomNetworkingClient:
    def invoke_request(self, name: str, request: dict) -> dict:
        if name == "get_temperature":
            return self._mock_network_response({"temperature": random.randint(60, 80)})
        elif name == "echo_request":
            return self._mock_network_response({"foo": "bar", "request": request})
        elif name == "fibonacci":
            return self._mock_network_response({"data": [1, 1, 2, 3, 5, 8]})
        else:
            raise ValueError(f"Invalid tool name: {name}")

    def _mock_network_response(self, response: dict, latency: int = 1) -> dict:
        time.sleep(latency)  # Simulate network latency
        return response
