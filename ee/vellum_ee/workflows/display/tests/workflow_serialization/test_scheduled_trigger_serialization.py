from contextlib import contextmanager
import json
import os
import tempfile
from unittest.mock import patch
from uuid import UUID
from typing import Iterator, Tuple

from deepdiff import DeepDiff

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.base import _get_trigger_path_to_id_mapping
from vellum.workflows.triggers.schedule import ScheduleTrigger
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.editor import NodeDisplayComment
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


@contextmanager
def mock_metadata_json(trigger_class_name: str, trigger_id: UUID) -> Iterator[Tuple[str, UUID]]:
    """
    Context manager that mocks metadata.json with trigger ID mapping.

    Args:
        trigger_class_name: Name of the trigger class (e.g., "DailyScheduleTrigger")
        trigger_id: The UUID to map the trigger to

    Yields:
        Tuple of (trigger_module_path, trigger_id)
    """
    # Create a temporary directory to simulate a workflow module
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create metadata.json with trigger mapping
        metadata_path = os.path.join(tmpdir, "metadata.json")

        test_module_parts = __name__.split(".")
        workflow_root_module = ".".join(test_module_parts[:-1])  # Remove last part

        relative_module_path = "." + test_module_parts[-1]
        # Include the full trigger path with class name to match TypeScript codegen
        relative_trigger_path = f"{relative_module_path}.{trigger_class_name}"

        with open(metadata_path, "w") as f:
            json.dump(
                {
                    "trigger_path_to_id_mapping": {
                        # Use full trigger path including class name
                        relative_trigger_path: str(trigger_id),
                    }
                },
                f,
            )

        # Create a custom mock for virtual_open that returns our tmpdir file
        def mock_virtual_open(path):
            # Regardless of the path requested, return our test metadata.json
            return open(metadata_path)

        # Mock the workflow root finder to return the parent module path
        with patch(
            "vellum.workflows.triggers.base._find_workflow_root_with_metadata", return_value=workflow_root_module
        ):
            with patch("vellum.workflows.triggers.base.virtual_open", side_effect=mock_virtual_open):
                # Clear the LRU cache to ensure fresh read
                _get_trigger_path_to_id_mapping.cache_clear()

                yield __name__, trigger_id


def test_scheduled_trigger_serialization_with_metadata_json():
    """ScheduleTrigger uses mapped ID from metadata.json when available."""

    # GIVEN we have an expected trigger ID
    expected_trigger_id = UUID("12345678-1234-1234-1234-123456789abc")

    # AND we have metadata.json set up with the trigger mapping
    with mock_metadata_json(
        "test_scheduled_trigger_serialization_with_metadata_json.<locals>.DailyScheduleTrigger",
        expected_trigger_id,
    ):

        class DailyScheduleTrigger(ScheduleTrigger):
            class Config(ScheduleTrigger.Config):
                cron = "0 9 * * *"  # Every day at 9am
                timezone = "America/New_York"

        class ProcessNode(BaseNode):
            class Outputs(BaseNode.Outputs):
                timestamp = DailyScheduleTrigger.current_run_at

            def run(self) -> Outputs:
                return self.Outputs()

        # AND a workflow that has the scheduled trigger as the entrypoint
        class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
            graph = DailyScheduleTrigger >> ProcessNode

        # WHEN we serialize the workflow
        # The trigger ID should be automatically loaded from metadata.json by the metaclass
        result: dict = get_workflow_display(workflow_class=TestWorkflow).serialize()

        # THEN we get the expected trigger
        assert "triggers" in result
        triggers = result["triggers"]
        assert isinstance(triggers, list)
        assert len(triggers) == 1

        trigger = triggers[0]
        assert isinstance(trigger, dict)
        assert trigger["type"] == "SCHEDULED"

        # AND the id is the one from metadata.json
        assert trigger["id"] == str(expected_trigger_id)


def test_scheduled_trigger_serialization_without_metadata_json():
    """ScheduleTrigger uses default hash-based __id__ when no metadata.json is available."""

    # GIVEN a scheduled trigger defined without metadata.json
    class WeeklyScheduleTrigger(ScheduleTrigger):
        class Config(ScheduleTrigger.Config):
            cron = "0 9 * * MON"  # Every Monday at 9am
            timezone = "UTC"

    class ProcessNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            timestamp = WeeklyScheduleTrigger.current_run_at

        def run(self) -> Outputs:
            return self.Outputs()

    # AND a workflow that has the scheduled trigger as the entrypoint
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = WeeklyScheduleTrigger >> ProcessNode

    # WHEN we serialize the workflow without metadata.json
    result: dict = get_workflow_display(workflow_class=TestWorkflow).serialize()

    # THEN we get the expected trigger
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1

    trigger = triggers[0]
    assert isinstance(trigger, dict)
    assert trigger["type"] == "SCHEDULED"

    # AND the id is the trigger class's default __id__ (hash-based)
    expected_module_path = (
        f"{__name__}.test_scheduled_trigger_serialization_without_metadata_json.<locals>.WeeklyScheduleTrigger"
    )
    expected_default_id = str(uuid4_from_hash(expected_module_path))
    assert trigger["id"] == expected_default_id

    # AND attributes are serialized
    assert "attributes" in trigger
    attributes = trigger["attributes"]
    assert isinstance(attributes, list)


def test_scheduled_trigger_serialization_display_data():
    """ScheduleTrigger with Display class serializes all display attributes correctly."""

    # GIVEN a scheduled trigger with comprehensive Display attributes
    class DailyTriggerWithDisplay(ScheduleTrigger):
        class Config(ScheduleTrigger.Config):
            cron = "0 9 * * *"
            timezone = "UTC"

        class Display(ScheduleTrigger.Display):
            label = "Daily Schedule"
            x = 100.5
            y = 200.75
            z_index = 3
            icon = "vellum:icon:calendar"
            color = "#4A90E2"

    class ProcessNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            timestamp = DailyTriggerWithDisplay.current_run_at

        def run(self) -> Outputs:
            return self.Outputs()

    # AND a workflow that uses the trigger
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = DailyTriggerWithDisplay >> ProcessNode

    # WHEN we serialize the workflow
    result: dict = get_workflow_display(workflow_class=TestWorkflow).serialize()

    # THEN we get the expected trigger
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1

    trigger = triggers[0]
    assert isinstance(trigger, dict)
    assert trigger["type"] == "SCHEDULED"

    # AND display_data is serialized with icon and color
    assert "display_data" in trigger
    display_data = trigger["display_data"]
    assert isinstance(display_data, dict)
    assert display_data["icon"] == "vellum:icon:calendar"
    assert display_data["color"] == "#4A90E2"


def test_scheduled_trigger_serialization_full():
    # GIVEN a scheduled trigger with comprehensive Display attributes
    class DailyTriggerWithDisplay(ScheduleTrigger):
        class Config(ScheduleTrigger.Config):
            cron = "0 9 * * *"
            timezone = "UTC"

        class Display(ScheduleTrigger.Display):
            label = "Daily Schedule"
            x = 100.5
            y = 200.75
            z_index = 3
            icon = "vellum:icon:calendar"
            color = "#4A90E2"
            comment = NodeDisplayComment(value="This is scheduled trigger", expanded=True)

    class ProcessNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            timestamp = DailyTriggerWithDisplay.current_run_at

        def run(self) -> Outputs:
            return self.Outputs()

    # AND a workflow that uses the trigger
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = DailyTriggerWithDisplay >> ProcessNode

    # WHEN we serialize the workflow
    result: dict = get_workflow_display(workflow_class=TestWorkflow).serialize()

    # THEN we get the expected trigger
    assert len(result["triggers"]) == 1
    trigger = result["triggers"][0]

    # AND the trigger has the expected structure with attributes
    assert trigger["id"] == "f3e5eddb-75da-42e6-9abf-d616f30c145c"
    assert trigger["type"] == "SCHEDULED"
    assert trigger["cron"] == "0 9 * * *"
    assert trigger["timezone"] == "UTC"

    # AND attributes are serialized (current_run_at and next_run_at from ScheduleTrigger)
    assert "attributes" in trigger
    attributes = trigger["attributes"]
    assert isinstance(attributes, list)
    assert len(attributes) == 2
    attribute_keys = {attr["key"] for attr in attributes}
    assert attribute_keys == {"current_run_at", "next_run_at"}

    # AND display_data is serialized correctly
    assert not DeepDiff(
        trigger["display_data"],
        {
            "label": "Daily Schedule",
            "position": {"x": 100.5, "y": 200.75},
            "z_index": 3,
            "icon": "vellum:icon:calendar",
            "color": "#4A90E2",
            "comment": {
                "value": "This is scheduled trigger",
                "expanded": True,
            },
        },
    )
