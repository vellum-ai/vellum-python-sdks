from typing import Dict, List, Type

from .base import SearchEngineBase
from .brave import BraveEngine
from .serpapi import SerpAPIEngine


class SearchEngineFactory:
    """
    Factory for creating search engine instances.

    Manages the registry of available search engines and provides
    a clean interface for engine instantiation.
    """

    _engines: Dict[str, Type[SearchEngineBase]] = {
        "serpapi": SerpAPIEngine,
        "brave": BraveEngine,
    }

    @classmethod
    def create_engine(cls, engine_name: str) -> SearchEngineBase:
        """
        Create a search engine instance by name.

        Args:
            engine_name: Name of the engine to create (e.g., "serpapi")

        Returns:
            SearchEngineBase instance

        Raises:
            ValueError: If engine_name is not supported
        """
        if engine_name not in cls._engines:
            available_engines = list(cls._engines.keys())
            raise ValueError(f"Unsupported search engine: {engine_name}. " f"Available engines: {available_engines}")

        engine_class = cls._engines[engine_name]
        return engine_class()

    @classmethod
    def get_available_engines(cls) -> List[str]:
        """Get list of available engine names."""
        return list(cls._engines.keys())

    @classmethod
    def register_engine(cls, engine_name: str, engine_class: Type[SearchEngineBase]) -> None:
        """
        Register a new search engine.

        Args:
            engine_name: Unique name for the engine
            engine_class: Engine class that implements SearchEngineBase
        """
        cls._engines[engine_name] = engine_class
