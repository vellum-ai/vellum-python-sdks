from contextlib import contextmanager
import json
import os
import tempfile
from unittest.mock import patch
from uuid import UUID
from typing import Iterator, Tuple

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.base import _get_trigger_path_to_id_mapping
from vellum.workflows.triggers.schedule import ScheduleTrigger
from vellum.workflows.utils.uuids import uuid4_from_hash
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
        trigger_module_path = f"{__name__}.{trigger_class_name}"

        with open(metadata_path, "w") as f:
            json.dump(
                {
                    "trigger_path_to_id_mapping": {
                        trigger_module_path: str(trigger_id),
                    }
                },
                f,
            )

        # Mock the workflow root finder to return our temp directory
        # Mock os.path.exists to return True for our metadata.json
        with patch("vellum.workflows.triggers.base._find_workflow_root_with_metadata", return_value=tmpdir):
            with patch("vellum.workflows.triggers.base.os.path.exists", return_value=True):
                with patch("vellum.workflows.triggers.base.virtual_open", open):
                    # Clear the LRU cache to ensure fresh read
                    _get_trigger_path_to_id_mapping.cache_clear()

                    yield trigger_module_path, trigger_id


def test_scheduled_trigger_serialization_with_metadata_json():
    """ScheduleTrigger uses mapped ID from metadata.json when available."""

    # GIVEN we have an expected trigger ID
    expected_trigger_id = UUID("12345678-1234-1234-1234-123456789abc")

    # AND we have metadata.json set up with the trigger mapping
    # Note: Use the full qualified name including the test function name and <locals>
    with mock_metadata_json(
        "test_scheduled_trigger_serialization_with_metadata_json.<locals>.DailyScheduleTrigger",
        expected_trigger_id,
    ):
        # Define the trigger class AFTER setting up mocks
        # This ensures the metaclass reads from our mocked metadata.json
        class DailyScheduleTrigger(ScheduleTrigger):
            class Config:
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
        class Config:
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
