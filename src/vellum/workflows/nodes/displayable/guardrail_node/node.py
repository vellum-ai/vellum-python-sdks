from uuid import UUID
from typing import Any, ClassVar, Dict, Generic, List, Optional, Union, cast

from vellum import ChatHistoryInput, ChatMessage, JsonInput, MetricDefinitionInput, NumberInput, StringInput
from vellum.client import ApiError
from vellum.core import RequestOptions
from vellum.workflows.constants import LATEST_RELEASE_TAG
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.types.core import EntityInputsInterface, MergeBehavior
from vellum.workflows.types.generics import StateType


class GuardrailNode(BaseNode[StateType], Generic[StateType]):
    """
    Used to execute a Metric Definition and surface a float output representing the score.

    metric_definition: Union[UUID, str] - Either the Metric Definition's UUID or its name.
    metric_inputs: EntityInputsInterface - The inputs for the Metric
    release_tag: str - The release tag to use for the Metric
    request_options: Optional[RequestOptions] - The request options to use for the Metric
    """

    metric_definition: ClassVar[Union[UUID, str]]

    metric_inputs: ClassVar[EntityInputsInterface] = {}
    release_tag: str = LATEST_RELEASE_TAG

    request_options: Optional[RequestOptions] = None

    class Trigger(BaseNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY

    class Outputs(BaseOutputs):
        score: float
        normalized_score: Optional[float]
        log: Optional[str]
        reason: Optional[str]

    def run(self) -> Outputs:
        try:
            metric_execution = self._context.vellum_client.metric_definitions.execute_metric_definition(
                self.metric_definition if isinstance(self.metric_definition, str) else str(self.metric_definition),
                inputs=self._compile_metric_inputs(),
                release_tag=self.release_tag,
                request_options=self.request_options,
            )

        except ApiError:
            raise NodeException(
                code=WorkflowErrorCode.NODE_EXECUTION,
                message="Failed to execute metric definition",
            )

        metric_outputs = {output.name: output.value for output in metric_execution.outputs}
        SCORE_KEY = "score"
        NORMALIZED_SCORE_KEY = "normalized_score"
        LOG_KEY = "log"
        REASON_KEY = "reason"

        score = metric_outputs.get(SCORE_KEY)
        if not isinstance(score, float):
            raise NodeException(
                message=f"Metric execution must have one output named '{SCORE_KEY}' with type 'float'",
                code=WorkflowErrorCode.INVALID_OUTPUTS,
            )
        metric_outputs.pop(SCORE_KEY)

        if NORMALIZED_SCORE_KEY in metric_outputs:
            normalized_score = metric_outputs.pop(NORMALIZED_SCORE_KEY)
            if not isinstance(normalized_score, float):
                raise NodeException(
                    message=f"Metric execution must have one output named '{NORMALIZED_SCORE_KEY}' with type 'float'",
                    code=WorkflowErrorCode.INVALID_OUTPUTS,
                )
        else:
            normalized_score = None

        if LOG_KEY in metric_outputs:
            log = metric_outputs.pop(LOG_KEY) or ""
            if not isinstance(log, str):
                raise NodeException(
                    message="Metric execution log output must be of type 'str'",
                    code=WorkflowErrorCode.INVALID_OUTPUTS,
                )
        else:
            log = None

        if REASON_KEY in metric_outputs:
            reason = metric_outputs.pop(REASON_KEY) or ""
            if not isinstance(reason, str):
                raise NodeException(
                    message="Metric execution reason output must be of type 'str'",
                    code=WorkflowErrorCode.INVALID_OUTPUTS,
                )
        else:
            reason = None

        return self.Outputs(score=score, normalized_score=normalized_score, log=log, reason=reason, **metric_outputs)

    def _compile_metric_inputs(self) -> List[MetricDefinitionInput]:
        # TODO: We may want to consolidate with prompt deployment input compilation
        # https://app.shortcut.com/vellum/story/4117

        compiled_inputs: List[MetricDefinitionInput] = []

        for input_name, input_value in self.metric_inputs.items():
            if isinstance(input_value, str):
                compiled_inputs.append(
                    StringInput(
                        name=input_name,
                        value=input_value,
                    )
                )
            elif isinstance(input_value, list) and all(isinstance(message, ChatMessage) for message in input_value):
                compiled_inputs.append(
                    ChatHistoryInput(
                        name=input_name,
                        value=cast(List[ChatMessage], input_value),
                    )
                )
            elif isinstance(input_value, dict):
                compiled_inputs.append(
                    JsonInput(
                        name=input_name,
                        value=cast(Dict[str, Any], input_value),
                    )
                )
            elif isinstance(input_value, (int, float)):
                compiled_inputs.append(
                    NumberInput(
                        name=input_name,
                        value=input_value,
                    )
                )
            else:
                raise NodeException(
                    message=f"Unrecognized input type for input '{input_name}'",
                    code=WorkflowErrorCode.INVALID_INPUTS,
                )

        return compiled_inputs
