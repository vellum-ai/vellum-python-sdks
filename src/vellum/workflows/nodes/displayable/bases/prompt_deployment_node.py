import json
from uuid import UUID
from typing import Any, ClassVar, Dict, Generator, Generic, Iterator, List, Optional, Sequence, Union

from vellum import (
    ChatHistoryInputRequest,
    ChatMessage,
    ExecutePromptEvent,
    JsonInputRequest,
    PromptDeploymentExpandMetaRequest,
    PromptDeploymentInputRequest,
    PromptOutput,
    RawPromptExecutionOverridesRequest,
    StringInputRequest,
)
from vellum.client import ApiError, RequestOptions
from vellum.client.types.chat_message_request import ChatMessageRequest
from vellum.workflows.constants import LATEST_RELEASE_TAG, OMIT
from vellum.workflows.context import get_execution_context
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.errors.types import vellum_error_to_workflow_error
from vellum.workflows.events.types import default_serializer
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.displayable.bases.base_prompt_node import BasePromptNode
from vellum.workflows.outputs import BaseOutput
from vellum.workflows.types import MergeBehavior
from vellum.workflows.types.generics import StateType


class BasePromptDeploymentNode(BasePromptNode, Generic[StateType]):
    """
    Used to execute a Prompt Deployment.

    prompt_inputs: EntityInputsInterface - The inputs for the Prompt
    deployment: Union[UUID, str] - Either the Prompt Deployment's UUID or its name.
    release_tag: str - The release tag to use for the Prompt Execution
    external_id: Optional[str] - Optionally include a unique identifier for tracking purposes.
        Must be unique within a given Prompt Deployment.
    expand_meta: Optional[PromptDeploymentExpandMetaRequest] - Expandable execution fields to include in the response
    raw_overrides: Optional[RawPromptExecutionOverridesRequest] - The raw overrides to use for the Prompt Execution
    expand_raw: Optional[Sequence[str]] - Expandable raw fields to include in the response
    metadata: Optional[Dict[str, Optional[Any]]] - The metadata to use for the Prompt Execution
    request_options: Optional[RequestOptions] - The request options to use for the Prompt Execution
    ml_model_fallback: Optional[Sequence[str]] - ML model fallbacks to use
    """

    # Either the Prompt Deployment's UUID or its name.
    deployment: ClassVar[Union[UUID, str]]

    release_tag: str = LATEST_RELEASE_TAG
    external_id: Optional[str] = OMIT

    expand_meta: Optional[PromptDeploymentExpandMetaRequest] = OMIT
    raw_overrides: Optional[RawPromptExecutionOverridesRequest] = OMIT
    expand_raw: Optional[Sequence[str]] = OMIT
    metadata: Optional[Dict[str, Optional[Any]]] = OMIT
    ml_model_fallbacks: Optional[Sequence[str]] = OMIT

    class Trigger(BasePromptNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY

    def _get_prompt_event_stream(self, ml_model_fallback: Optional[str] = None) -> Iterator[ExecutePromptEvent]:
        execution_context = get_execution_context()
        request_options = self.request_options or RequestOptions()
        request_options["additional_body_parameters"] = {
            "execution_context": execution_context.model_dump(mode="json"),
            **request_options.get("additional_body_parameters", {}),
        }
        if ml_model_fallback:
            request_options["additional_body_parameters"] = {
                "overrides": {
                    "ml_model_fallback": ml_model_fallback,
                },
                **request_options.get("additional_body_parameters", {}),
            }

        return self._context.vellum_client.execute_prompt_stream(
            inputs=self._compile_prompt_inputs(),
            prompt_deployment_id=str(self.deployment) if isinstance(self.deployment, UUID) else None,
            prompt_deployment_name=self.deployment if isinstance(self.deployment, str) else None,
            release_tag=self.release_tag,
            external_id=self.external_id,
            expand_meta=self.expand_meta,
            raw_overrides=self.raw_overrides,
            expand_raw=self.expand_raw,
            metadata=self.metadata,
            request_options=request_options,
        )

    def _process_prompt_event_stream(self) -> Generator[BaseOutput, None, Optional[List[PromptOutput]]]:
        """Override the base prompt node _process_prompt_event_stream()"""
        self._validate()
        try:
            prompt_event_stream = self._get_prompt_event_stream()
        except ApiError:
            if self.ml_model_fallbacks:
                for ml_model_fallback in self.ml_model_fallbacks:
                    try:
                        prompt_event_stream = self._get_prompt_event_stream(ml_model_fallback=ml_model_fallback)
                        break
                    except ApiError:
                        continue
                else:
                    self._handle_api_error(
                        ApiError(
                            body={
                                "detail": f"Failed to execute prompts with these fallbacks: {self.ml_model_fallbacks}"
                            },
                            status_code=400,
                        )
                    )

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

    def _compile_prompt_inputs(self) -> List[PromptDeploymentInputRequest]:
        # TODO: We may want to consolidate with subworkflow deployment input compilation
        # https://app.shortcut.com/vellum/story/4117

        compiled_inputs: List[PromptDeploymentInputRequest] = []

        if not self.prompt_inputs:
            return compiled_inputs

        for input_name, input_value in self.prompt_inputs.items():
            if isinstance(input_value, str):
                compiled_inputs.append(
                    StringInputRequest(
                        name=input_name,
                        value=input_value,
                    )
                )
            elif (
                input_value
                and isinstance(input_value, list)
                and all(isinstance(message, (ChatMessage, ChatMessageRequest)) for message in input_value)
            ):
                chat_history = [
                    (
                        message
                        if isinstance(message, ChatMessageRequest)
                        else ChatMessageRequest.model_validate(message.model_dump())
                    )
                    for message in input_value
                    if isinstance(message, (ChatMessage, ChatMessageRequest))
                ]
                compiled_inputs.append(
                    ChatHistoryInputRequest(
                        name=input_name,
                        value=chat_history,
                    )
                )
            else:
                try:
                    input_value = default_serializer(input_value)
                except json.JSONDecodeError as e:
                    raise NodeException(
                        message=f"Failed to serialize input '{input_name}' of type '{input_value.__class__}': {e}",
                        code=WorkflowErrorCode.INVALID_INPUTS,
                    )

                compiled_inputs.append(
                    JsonInputRequest(
                        name=input_name,
                        value=input_value,
                    )
                )

        return compiled_inputs
