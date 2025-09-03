import pytest

from ...engines.brave import BraveEngine


@pytest.fixture
def brave_engine():
    """Create BraveEngine instance."""
    return BraveEngine()


def test_location_to_country_code_us_variations(brave_engine):
    """Test US location variations are converted to 'us'."""
    us_locations = [
        "United States",
        "USA",
        "US",
        "New York, NY",
        "California",
        "Texas",
        "new york, ny",  # case insensitive
        "UNITED STATES",
    ]

    for location in us_locations:
        result = brave_engine._location_to_country_code(location)
        assert result == "us", f"Failed for location: {location}"


def test_location_to_country_code_uk_variations(brave_engine):
    """Test UK location variations are converted to 'uk'."""
    uk_locations = [
        "United Kingdom",
        "UK",
        "England",
        "London",
        "united kingdom",  # case insensitive
        "LONDON",
    ]

    for location in uk_locations:
        result = brave_engine._location_to_country_code(location)
        assert result == "uk", f"Failed for location: {location}"


def test_location_to_country_code_canada_variations(brave_engine):
    """Test Canada location variations are converted to 'ca'."""
    canada_locations = [
        "Canada",
        "Toronto",
        "Vancouver",
        "canada",  # case insensitive
        "TORONTO",
    ]

    for location in canada_locations:
        result = brave_engine._location_to_country_code(location)
        assert result == "ca", f"Failed for location: {location}"


def test_location_to_country_code_australia_variations(brave_engine):
    """Test Australia location variations are converted to 'au'."""
    australia_locations = [
        "Australia",
        "Sydney",
        "Melbourne",
        "australia",  # case insensitive
        "SYDNEY",
    ]

    for location in australia_locations:
        result = brave_engine._location_to_country_code(location)
        assert result == "au", f"Failed for location: {location}"


def test_location_to_country_code_germany_variations(brave_engine):
    """Test Germany location variations are converted to 'de'."""
    germany_locations = [
        "Germany",
        "Deutschland",
        "Berlin",
        "germany",  # case insensitive
        "BERLIN",
    ]

    for location in germany_locations:
        result = brave_engine._location_to_country_code(location)
        assert result == "de", f"Failed for location: {location}"


def test_location_to_country_code_france_variations(brave_engine):
    """Test France location variations are converted to 'fr'."""
    france_locations = [
        "France",
        "Paris",
        "france",  # case insensitive
        "PARIS",
    ]

    for location in france_locations:
        result = brave_engine._location_to_country_code(location)
        assert result == "fr", f"Failed for location: {location}"


def test_location_to_country_code_unknown_defaults_to_us(brave_engine):
    """Test unknown locations default to 'us'."""
    unknown_locations = [
        "Mars",
        "Unknown Place",
        "Atlantis",
        "",  # empty string
        "123456",  # numeric
    ]

    for location in unknown_locations:
        result = brave_engine._location_to_country_code(location)
        assert result == "us", f"Failed to default to 'us' for location: {location}"


def test_location_to_country_code_mixed_case_and_whitespace(brave_engine):
    """Test location conversion handles mixed case and whitespace."""
    test_cases = [
        ("  New York, NY  ", "us"),
        ("  LONDON  ", "uk"),
        (" toronto ", "ca"),
        ("Sydney, Australia", "au"),
        ("Berlin, Germany", "de"),
        ("Paris, France", "fr"),
    ]

    for location, expected in test_cases:
        result = brave_engine._location_to_country_code(location)
        assert result == expected, f"Failed for location: '{location}', expected '{expected}', got '{result}'"
