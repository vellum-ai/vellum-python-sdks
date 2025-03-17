from abc import abstractmethod
from typing import ClassVar, Generator, Generic, Iterator, List, Optional, Union

from vellum import AdHocExecutePromptEvent, ExecutePromptEvent, PromptOutput
from vellum.client.core.api_error import ApiError
from vellum.core import RequestOptions
from vellum.workflows.errors.types import WorkflowErrorCode, vellum_error_to_workflow_error
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs.base import BaseOutput, BaseOutputs
from vellum.workflows.types.core import EntityInputsInterface, MergeBehavior
from vellum.workflows.types.generics import StateType


class BasePromptNode(BaseNode, Generic[StateType]):
    # Inputs that are passed to the Prompt
    prompt_inputs: ClassVar[Optional[EntityInputsInterface]] = None

    request_options: Optional[RequestOptions] = None

    class Trigger(BaseNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY

    class Outputs(BaseOutputs):
        results: List[PromptOutput]

    @abstractmethod
    def _get_prompt_event_stream(self) -> Union[Iterator[AdHocExecutePromptEvent], Iterator[ExecutePromptEvent]]:
        pass

    def _validate(self) -> None:
        pass

    def run(self) -> Iterator[BaseOutput]:
        outputs = yield from self._process_prompt_event_stream()
        if outputs is None:
            raise NodeException(
                message="Expected to receive outputs from Prompt",
                code=WorkflowErrorCode.INTERNAL_ERROR,
            )

    def _process_prompt_event_stream(self) -> Generator[BaseOutput, None, Optional[List[PromptOutput]]]:
        self._validate()
        try:
            prompt_event_stream = self._get_prompt_event_stream()
        except ApiError as e:
            self._handle_api_error(e)

        # We don't use the INITIATED event anyway, so we can just skip it
        # and use the exception handling to catch other api level errors
        try:
            next(prompt_event_stream)
        except ApiError as e:
            self._handle_api_error(e)

        outputs: Optional[List[PromptOutput]] = None
        for event in prompt_event_stream:
            if event.state == "INITIATED":
                continue
            elif event.state == "STREAMING":
                yield BaseOutput(name="results", delta=event.output.value)
            elif event.state == "FULFILLED":
                outputs = event.outputs
                yield BaseOutput(name="results", value=event.outputs)
            elif event.state == "REJECTED":
                workflow_error = vellum_error_to_workflow_error(event.error)
                raise NodeException.of(workflow_error)

        return outputs

    def _handle_api_error(self, e: ApiError):
        if e.status_code and e.status_code >= 400 and e.status_code < 500 and isinstance(e.body, dict):
            raise NodeException(
                message=e.body.get("detail", "Failed to execute Prompt"),
                code=WorkflowErrorCode.INVALID_INPUTS,
            ) from e

        raise NodeException(
            message="Failed to execute Prompt",
            code=WorkflowErrorCode.INTERNAL_ERROR,
        ) from e
