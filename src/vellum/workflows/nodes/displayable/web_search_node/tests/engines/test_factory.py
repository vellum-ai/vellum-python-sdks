import pytest

from ...engines.base import SearchEngineBase
from ...engines.brave import BraveEngine
from ...engines.factory import SearchEngineFactory
from ...engines.serpapi import SerpAPIEngine


def test_create_serpapi_engine():
    """Test creating SerpAPI engine via factory."""
    # WHEN we create a SerpAPI engine
    engine = SearchEngineFactory.create_engine("serpapi")

    # THEN it should be the correct type
    assert isinstance(engine, SerpAPIEngine)
    assert isinstance(engine, SearchEngineBase)


def test_create_invalid_engine():
    """Test creating invalid engine raises ValueError."""
    # WHEN we try to create an unsupported engine
    with pytest.raises(ValueError) as exc_info:
        SearchEngineFactory.create_engine("unsupported_engine")

    # THEN it should raise an appropriate error
    assert "Unsupported search engine: unsupported_engine" in str(exc_info.value)
    assert "Available engines:" in str(exc_info.value)
    assert "serpapi" in str(exc_info.value)
    assert "brave" in str(exc_info.value)


def test_create_brave_engine():
    """Test creating Brave engine via factory."""
    # WHEN we create a Brave engine
    engine = SearchEngineFactory.create_engine("brave")

    # THEN it should be the correct type
    assert isinstance(engine, BraveEngine)
    assert isinstance(engine, SearchEngineBase)


def test_get_available_engines():
    """Test getting list of available engines."""
    # WHEN we get available engines
    engines = SearchEngineFactory.get_available_engines()

    # THEN it should return the correct list
    assert set(engines) == {"serpapi", "brave"}


def test_register_new_engine():
    """Test registering a new engine dynamically."""

    # GIVEN a mock engine class
    class MockEngine(SearchEngineBase):
        def search(self, query, api_key, num_results, location, context):
            return {"text": "mock", "urls": [], "results": []}

    # WHEN we register a new engine
    SearchEngineFactory.register_engine("mock", MockEngine)

    # THEN it should be available
    assert "mock" in SearchEngineFactory.get_available_engines()

    # AND we should be able to create it
    engine = SearchEngineFactory.create_engine("mock")
    assert isinstance(engine, MockEngine)

    # Clean up
    del SearchEngineFactory._engines["mock"]
