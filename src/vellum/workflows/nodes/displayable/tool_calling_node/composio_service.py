from dataclasses import dataclass
from typing import List

from composio_client import Composio as ComposioClient


@dataclass
class ConnectionInfo:
    """Information about a user's authorized connection"""

    connection_id: str
    integration_name: str
    created_at: str
    updated_at: str
    status: str = "ACTIVE"  # TODO: Use enum if we end up supporting integrations that the user has not yet connected to


class ComposioAccountService:
    """Manages user authorized connections using composio-client"""

    def __init__(self, api_key: str):
        self.client = ComposioClient(api_key=api_key)

    def get_user_connections(self) -> List[ConnectionInfo]:
        """Get all authorized connections for the user"""
        response = self.client.connected_accounts.list()

        return [
            ConnectionInfo(
                connection_id=item.id,
                integration_name=item.toolkit.slug,
                status=item.status,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in response.items
        ]


class ComposioService:
    """Unified interface for Composio operations"""

    def __init__(self, api_key: str):
        self.accounts = ComposioAccountService(api_key)

    def get_user_connections(self) -> List[ConnectionInfo]:
        """Get user's authorized connections"""
        return self.accounts.get_user_connections()
