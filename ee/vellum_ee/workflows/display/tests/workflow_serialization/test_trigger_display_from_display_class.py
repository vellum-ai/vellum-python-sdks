"""Tests for BaseTrigger.Display serialization."""

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.schedule import ScheduleTrigger
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_serialize_basetrigger_with_display_class():
    """Tests that BaseTrigger.Display class attributes serialize correctly."""

    class MyTrigger(ScheduleTrigger):
        class Config:
            cron = "0 9 * * *"
            timezone = "UTC"

        class Display:
            icon = "vellum:icon:gear"
            color = "purple"

    class SimpleNode(BaseNode):
        pass

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = MyTrigger >> SimpleNode

    # WHEN we serialize the workflow
    result: dict = get_workflow_display(workflow_class=TestWorkflow).serialize()

    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1

    trigger = triggers[0]
    assert isinstance(trigger, dict)
    assert "display_data" in trigger
    display_data = trigger["display_data"]
    assert isinstance(display_data, dict)
    assert display_data["icon"] == "vellum:icon:gear"
    assert display_data["color"] == "purple"


def test_serialize_trigger_with_only_icon():
    """Tests that triggers with only icon serialize correctly."""

    class IconOnlyTrigger(ScheduleTrigger):
        class Config:
            cron = "0 9 * * *"
            timezone = "UTC"

        class Display:
            icon = "vellum:icon:star"

    class SimpleNode(BaseNode):
        pass

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = IconOnlyTrigger >> SimpleNode

    # WHEN we serialize the workflow
    result: dict = get_workflow_display(workflow_class=TestWorkflow).serialize()

    triggers = result["triggers"]
    assert len(triggers) == 1
    trigger = triggers[0]
    display_data = trigger["display_data"]
    assert display_data["icon"] == "vellum:icon:star"
    assert "color" not in display_data


def test_serialize_trigger_with_only_color():
    """Tests that triggers with only color serialize correctly."""

    class ColorOnlyTrigger(ScheduleTrigger):
        class Config:
            cron = "0 9 * * *"
            timezone = "UTC"

        class Display:
            color = "#FF5733"

    class SimpleNode(BaseNode):
        pass

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = ColorOnlyTrigger >> SimpleNode

    # WHEN we serialize the workflow
    result: dict = get_workflow_display(workflow_class=TestWorkflow).serialize()

    triggers = result["triggers"]
    assert len(triggers) == 1
    trigger = triggers[0]
    display_data = trigger["display_data"]
    assert display_data["color"] == "#FF5733"
    assert "icon" not in display_data


def test_serialize_trigger_without_display_class():
    """Tests that triggers without Display class don't have display_data."""

    class PlainTrigger(ScheduleTrigger):
        class Config:
            cron = "0 9 * * *"
            timezone = "UTC"

    class SimpleNode(BaseNode):
        pass

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = PlainTrigger >> SimpleNode

    # WHEN we serialize the workflow
    result: dict = get_workflow_display(workflow_class=TestWorkflow).serialize()

    triggers = result["triggers"]
    assert len(triggers) == 1
    trigger = triggers[0]
    display_data = trigger.get("display_data")
    if display_data is not None:
        assert display_data == {}


def test_serialize_trigger_with_none_values():
    """Tests that triggers with None icon/color don't serialize those fields."""

    class NoneValuesTrigger(ScheduleTrigger):
        class Config:
            cron = "0 9 * * *"
            timezone = "UTC"

        class Display:
            icon = None
            color = None

    class SimpleNode(BaseNode):
        pass

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = NoneValuesTrigger >> SimpleNode

    # WHEN we serialize the workflow
    result: dict = get_workflow_display(workflow_class=TestWorkflow).serialize()

    triggers = result["triggers"]
    assert len(triggers) == 1
    trigger = triggers[0]
    display_data = trigger.get("display_data")
    if display_data is not None:
        assert display_data == {}
