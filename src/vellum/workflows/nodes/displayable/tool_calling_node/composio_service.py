from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional

from composio_client import Composio as ComposioClient


class ConnectionStatus(Enum):
    """Status of a user's connection to a service"""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DISABLED = "DISABLED"


@dataclass
class ConnectionInfo:
    """Information about a user's authorized connection"""

    connection_id: str
    integration_name: str
    status: ConnectionStatus
    created_at: str
    updated_at: str


@dataclass
class ToolExecutionResult:
    """Result of a tool execution"""

    success: bool
    data: Any = None
    error: Optional[str] = None


class ComposioAccountService:
    """Manages user authorized connections using composio-client"""

    def __init__(self, api_key: str):
        self._client = ComposioClient(api_key=api_key)

    def get_user_connections(self) -> List[ConnectionInfo]:
        """Get all authorized connections for the user"""
        response = self._client.connected_accounts.list()

        return [
            ConnectionInfo(
                connection_id=item.id,
                integration_name=item.toolkit.slug,
                status=ConnectionStatus(item.status),
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
