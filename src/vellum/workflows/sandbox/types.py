from typing import Any, Dict, Generic, TypeVar

from pydantic import field_serializer

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.events.types import default_serializer
from vellum.workflows.inputs.base import BaseInputs

# We define a new generic instead of importing from generics.py
# because we need BaseInputs to be defined on import
WorkflowInputsType = TypeVar("WorkflowInputsType", bound=BaseInputs)


class Datapoint(UniversalBaseModel, Generic[WorkflowInputsType]):
    name: str
    inputs: WorkflowInputsType

    @field_serializer("inputs")
    def serialize_inputs(self, inputs: WorkflowInputsType, _info: Any) -> Dict[str, Any]:
        return default_serializer(inputs)
