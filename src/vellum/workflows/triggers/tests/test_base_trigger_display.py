"""Tests for BaseTrigger.Display nested class."""

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.triggers.base import BaseTrigger
from vellum.workflows.triggers.integration import IntegrationTrigger


def test_base_trigger__has_display_class():
    """
    Tests that BaseTrigger has a Display nested class with default attributes.
    """

    display_class = BaseTrigger.Display

    assert display_class is not None
    assert hasattr(display_class, "label")
    assert hasattr(display_class, "x")
    assert hasattr(display_class, "y")
    assert hasattr(display_class, "z_index")
    assert hasattr(display_class, "icon")
    assert hasattr(display_class, "color")

    assert display_class.label == "Trigger"
    assert display_class.x == 0.0
    assert display_class.y == 0.0
    assert display_class.z_index == 0.0
    assert display_class.icon is None
    assert display_class.color is None


def test_base_trigger__display_class_inheritance():
    """
    Tests that trigger subclasses automatically inherit Display class.
    """

    class CustomTrigger(IntegrationTrigger):
        class Config(IntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "test"
            slug = "test"

    display_class = CustomTrigger.Display

    assert display_class is not None
    assert issubclass(display_class, BaseTrigger.Display)

    assert hasattr(display_class, "label")
    assert hasattr(display_class, "x")
    assert hasattr(display_class, "y")
    assert hasattr(display_class, "z_index")
    assert hasattr(display_class, "icon")
    assert hasattr(display_class, "color")


def test_base_trigger__display_class_can_be_overridden():
    """
    Tests that trigger subclasses can override Display class attributes.
    """

    class CustomTrigger(IntegrationTrigger):
        class Config(IntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "test"
            slug = "test"

        class Display(IntegrationTrigger.Display):
            label = "Custom Trigger"
            icon = "🎨"
            color = "#FF5733"

    display_class = CustomTrigger.Display

    assert display_class.label == "Custom Trigger"
    assert display_class.icon == "🎨"
    assert display_class.color == "#FF5733"

    assert display_class.x == 0.0
    assert display_class.y == 0.0
    assert display_class.z_index == 0.0


def test_base_trigger__display_class_multi_level_inheritance():
    """
    Tests that Display class inheritance works across multiple levels.
    """

    class MiddleTrigger(IntegrationTrigger):
        class Config(IntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "test"
            slug = "test"

        class Display(IntegrationTrigger.Display):
            label = "Middle Trigger"
            icon = "🔧"

    class LeafTrigger(MiddleTrigger):
        class Config(MiddleTrigger.Config):
            slug = "leaf_test"

    display_class = LeafTrigger.Display

    assert issubclass(display_class, MiddleTrigger.Display)
    assert issubclass(display_class, BaseTrigger.Display)

    assert display_class.label == "Middle Trigger"
    assert display_class.icon == "🔧"

    assert display_class.x == 0.0
    assert display_class.y == 0.0
    assert display_class.z_index == 0.0
    assert display_class.color is None


def test_base_trigger__display_class_override_in_leaf():
    """
    Tests that leaf triggers can override Display attributes from parent.
    """

    class MiddleTrigger(IntegrationTrigger):
        class Config(IntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "test"
            slug = "test"

        class Display(IntegrationTrigger.Display):
            label = "Middle Trigger"
            icon = "🔧"

    class LeafTrigger(MiddleTrigger):
        class Config(MiddleTrigger.Config):
            slug = "leaf_test"

        class Display(MiddleTrigger.Display):
            label = "Leaf Trigger"
            color = "#00FF00"

    display_class = LeafTrigger.Display

    assert display_class.label == "Leaf Trigger"
    assert display_class.color == "#00FF00"

    assert display_class.icon == "🔧"

    assert display_class.x == 0.0
    assert display_class.y == 0.0
    assert display_class.z_index == 0.0
