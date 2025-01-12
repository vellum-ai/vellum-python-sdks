from typing import Sequence, Union

from pydantic import ConfigDict

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.outputs.base import BaseOutputs


class MockNodeExecution(UniversalBaseModel):
    when_condition: BaseDescriptor
    then_outputs: BaseOutputs

    model_config = ConfigDict(arbitrary_types_allowed=True)


MockNodeExecutionArg = Sequence[Union[BaseOutputs, MockNodeExecution]]
