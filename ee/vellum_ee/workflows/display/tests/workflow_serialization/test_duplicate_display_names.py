from uuid import uuid4
from typing import cast

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


class TestDuplicateDisplayNames:
    """Test that duplicate display names get unique identifiers appended."""

    def test_duplicate_input_names_get_unique_keys(self):
        """Test that duplicate input names get unique keys with appended IDs."""

        class TestInputs(BaseInputs):
            input_a: str
            input_b: str

        class TestWorkflow(BaseWorkflow):
            class Inputs(TestInputs):
                pass

        workflow_display = BaseWorkflowDisplay[TestWorkflow]()

        from vellum.workflows.references.workflow_input import WorkflowInputReference
        from vellum_ee.workflows.display.base import WorkflowInputsDisplay

        input_ref_a = WorkflowInputReference(name="input_a", types=(str,), instance=None, inputs_class=TestInputs)
        input_ref_b = WorkflowInputReference(name="input_b", types=(str,), instance=None, inputs_class=TestInputs)

        display_a = WorkflowInputsDisplay(id=uuid4(), name="duplicate_name")
        display_b = WorkflowInputsDisplay(id=uuid4(), name="duplicate_name")

        workflow_display.display_context.workflow_input_displays = {
            input_ref_a: display_a,
            input_ref_b: display_b,
        }

        result = workflow_display.serialize()

        input_variables = cast(JsonArray, result["input_variables"])
        assert len(input_variables) == 2

        keys = [cast(JsonObject, var)["key"] for var in input_variables]
        assert len(set(keys)) == 2  # All keys should be unique

        for key in keys:
            key_str = cast(str, key)
            assert key_str.startswith("duplicate_name_")
            assert len(key_str) > len("duplicate_name_")

    def test_duplicate_output_names_get_unique_keys(self):
        """Test that duplicate output names get unique keys with appended IDs."""

        class TestOutputs(BaseOutputs):
            output_a: str
            output_b: str

        class TestWorkflow(BaseWorkflow):
            class Outputs(TestOutputs):
                pass

        workflow_display = BaseWorkflowDisplay[TestWorkflow]()

        from vellum.workflows.references.output import OutputReference
        from vellum_ee.workflows.display.base import WorkflowOutputDisplay

        output_ref_a = OutputReference(name="output_a", types=(str,), instance=None, outputs_class=TestOutputs)
        output_ref_b = OutputReference(name="output_b", types=(str,), instance=None, outputs_class=TestOutputs)

        display_a = WorkflowOutputDisplay(id=uuid4(), name="duplicate_output")
        display_b = WorkflowOutputDisplay(id=uuid4(), name="duplicate_output")

        workflow_display.display_context.workflow_output_displays = {
            output_ref_a: display_a,
            output_ref_b: display_b,
        }

        result = workflow_display.serialize()

        output_variables = cast(JsonArray, result["output_variables"])
        assert len(output_variables) == 2

        keys = [cast(JsonObject, var)["key"] for var in output_variables]
        assert len(set(keys)) == 2  # All keys should be unique

        for key in keys:
            key_str = cast(str, key)
            assert key_str.startswith("duplicate_output_")
            assert len(key_str) > len("duplicate_output_")

    def test_unique_names_remain_unchanged(self):
        """Test that unique names remain unchanged."""

        class TestInputs(BaseInputs):
            unique_input: str

        class TestOutputs(BaseOutputs):
            unique_output: str

        class TestWorkflow(BaseWorkflow):
            class Inputs(TestInputs):
                pass

            class Outputs(TestOutputs):
                pass

        workflow_display = BaseWorkflowDisplay[TestWorkflow]()

        from vellum.workflows.references.output import OutputReference
        from vellum.workflows.references.workflow_input import WorkflowInputReference
        from vellum_ee.workflows.display.base import WorkflowInputsDisplay, WorkflowOutputDisplay

        input_ref = WorkflowInputReference(name="unique_input", types=(str,), instance=None, inputs_class=TestInputs)
        output_ref = OutputReference(name="unique_output", types=(str,), instance=None, outputs_class=TestOutputs)

        input_display = WorkflowInputsDisplay(id=uuid4(), name="unique_input_name")
        output_display = WorkflowOutputDisplay(id=uuid4(), name="unique_output_name")

        workflow_display.display_context.workflow_input_displays = {input_ref: input_display}
        workflow_display.display_context.workflow_output_displays = {output_ref: output_display}

        result = workflow_display.serialize()

        input_variables = cast(JsonArray, result["input_variables"])
        assert len(input_variables) == 1
        assert cast(JsonObject, input_variables[0])["key"] == "unique_input_name"

        output_variables = cast(JsonArray, result["output_variables"])
        assert len(output_variables) == 1
        assert cast(JsonObject, output_variables[0])["key"] == "unique_output_name"

    def test_mixed_duplicate_and_unique_names(self):
        """Test handling of mixed duplicate and unique names."""

        class TestInputs(BaseInputs):
            input_a: str
            input_b: str
            input_c: str

        class TestWorkflow(BaseWorkflow):
            class Inputs(TestInputs):
                pass

        workflow_display = BaseWorkflowDisplay[TestWorkflow]()

        from vellum.workflows.references.workflow_input import WorkflowInputReference
        from vellum_ee.workflows.display.base import WorkflowInputsDisplay

        input_refs = [
            WorkflowInputReference(name=f"input_{i}", types=(str,), instance=None, inputs_class=TestInputs)
            for i in ["a", "b", "c"]
        ]

        displays = [
            WorkflowInputsDisplay(id=uuid4(), name="duplicate_name"),  # duplicate
            WorkflowInputsDisplay(id=uuid4(), name="duplicate_name"),  # duplicate
            WorkflowInputsDisplay(id=uuid4(), name="unique_name"),  # unique
        ]

        workflow_display.display_context.workflow_input_displays = dict(zip(input_refs, displays))

        result = workflow_display.serialize()

        input_variables = cast(JsonArray, result["input_variables"])
        assert len(input_variables) == 3

        keys = [cast(JsonObject, var)["key"] for var in input_variables]
        assert len(set(keys)) == 3  # All keys should be unique

        unique_keys = [key for key in keys if key == "unique_name"]
        assert len(unique_keys) == 1

        duplicate_keys = [key for key in keys if cast(str, key).startswith("duplicate_name_")]
        assert len(duplicate_keys) == 2
