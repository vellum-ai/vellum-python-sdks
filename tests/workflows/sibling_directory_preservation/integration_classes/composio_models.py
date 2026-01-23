"""
Composio integration models for testing sibling directory preservation.

This file exists to verify that sibling directories next to `nodes` are not
deleted during codegen operations.
"""

from pydantic import BaseModel


class ComposioResponse(BaseModel):
    """Example Pydantic model that a user might define in a sibling directory."""

    status: str
    data: dict
