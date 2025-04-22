from abc import abstractmethod
from typing import ClassVar, Generator, Generic, Iterator, List, Optional, Union

from vellum import AdHocExecutePromptEvent, ExecutePromptEvent, PromptOutput
from vellum.client.core.api_error import ApiError
from vellum.core import RequestOptions
from vellum.workflows.errors.types import WorkflowErrorCode
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

    @abstractmethod
    def _process_prompt_event_stream(self) -> Generator[BaseOutput, None, Optional[List[PromptOutput]]]:
        pass

    def _handle_api_error(self, e: ApiError):
        if e.status_code and e.status_code == 403 and isinstance(e.body, dict):
            raise NodeException(
                message=e.body.get("detail", "Provider credentials is missing or unavailable"),
                code=WorkflowErrorCode.PROVIDER_CREDENTIALS_UNAVAILABLE,
            )

        elif e.status_code and e.status_code >= 400 and e.status_code < 500 and isinstance(e.body, dict):
            raise NodeException(
                message=e.body.get("detail", "Failed to execute Prompt"),
                code=WorkflowErrorCode.INVALID_INPUTS,
            ) from e

        raise NodeException(
            message="Failed to execute Prompt",
            code=WorkflowErrorCode.INTERNAL_ERROR,
        ) from e
