from typing import Any

from .mock_networking_client import MockNetworkingClient
from .my_prompt import MyPrompt


class Fibonacci(MockNetworkingClient):
    action = MyPrompt.Outputs.results[0]["value"]

    class Outputs(MockNetworkingClient.Outputs):
        response: Any

    "A node that calls our base Mock Networking Client"
