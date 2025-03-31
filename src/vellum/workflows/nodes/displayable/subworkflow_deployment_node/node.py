import json
from uuid import UUID
from typing import Any, ClassVar, Dict, Generic, Iterator, List, Optional, Set, Union, cast

from vellum import (
    ChatMessage,
    WorkflowExpandMetaRequest,
    WorkflowOutput,
    WorkflowRequestChatHistoryInputRequest,
    WorkflowRequestInputRequest,
    WorkflowRequestJsonInputRequest,
    WorkflowRequestNumberInputRequest,
    WorkflowRequestStringInputRequest,
)
from vellum.client.core.api_error import ApiError
from vellum.client.types.chat_message_request import ChatMessageRequest
from vellum.core import RequestOptions
from vellum.workflows.constants import LATEST_RELEASE_TAG, OMIT
from vellum.workflows.context import get_execution_context
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.errors.types import workflow_event_error_to_workflow_error
from vellum.workflows.events.types import default_serializer
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.types.core import EntityInputsInterface, MergeBehavior
from vellum.workflows.types.generics import StateType


class SubworkflowDeploymentNode(BaseNode[StateType], Generic[StateType]):
    """
    Used to execute a Workflow Deployment.

    subworkflow_inputs: EntityInputsInterface - The inputs for the Subworkflow
    deployment: Union[UUID, str] - Either the Workflow Deployment's UUID or its name.
    release_tag: str = LATEST_RELEASE_TAG - The release tag to use for the Workflow Execution
    external_id: Optional[str] = OMIT - Optionally include a unique identifier for tracking purposes.
        Must be unique within a given Workflow Deployment.
    expand_meta: Optional[WorkflowExpandMetaRequest] = OMIT - Expandable execution fields to include in the response
    metadata: Optional[Dict[str, Optional[Any]]] = OMIT - The metadata to use for the Workflow Execution
    request_options: Optional[RequestOptions] = None - The request options to use for the Workflow Execution
    """

    # Either the Workflow Deployment's UUID or its name.
    deployment: ClassVar[Union[UUID, str]]
    subworkflow_inputs: ClassVar[EntityInputsInterface] = {}

    release_tag: str = LATEST_RELEASE_TAG
    external_id: Optional[str] = OMIT

    expand_meta: Optional[WorkflowExpandMetaRequest] = OMIT
    metadata: Optional[Dict[str, Optional[Any]]] = OMIT

    request_options: Optional[RequestOptions] = None

    class Trigger(BaseNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY

    def _compile_subworkflow_inputs(self) -> List[WorkflowRequestInputRequest]:
        # TODO: We may want to consolidate with prompt deployment input compilation
        # https://app.shortcut.com/vellum/story/4117

        compiled_inputs: List[WorkflowRequestInputRequest] = []

        for input_name, input_value in self.subworkflow_inputs.items():
            if isinstance(input_value, str):
                compiled_inputs.append(
                    WorkflowRequestStringInputRequest(
                        name=input_name,
                        value=input_value,
                    )
                )
            elif (
                isinstance(input_value, list)
                and len(input_value) > 0
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
                    WorkflowRequestChatHistoryInputRequest(
                        name=input_name,
                        value=chat_history,
                    )
                )
            elif isinstance(input_value, dict):
                compiled_inputs.append(
                    WorkflowRequestJsonInputRequest(
                        name=input_name,
                        value=cast(Dict[str, Any], input_value),
                    )
                )
            elif isinstance(input_value, (int, float)):
                compiled_inputs.append(
                    WorkflowRequestNumberInputRequest(
                        name=input_name,
                        value=input_value,
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
                    WorkflowRequestJsonInputRequest(
                        name=input_name,
                        value=input_value,
                    )
                )

        return compiled_inputs

    def run(self) -> Iterator[BaseOutput]:
        execution_context = get_execution_context()
        request_options = self.request_options or RequestOptions()
        request_options["additional_body_parameters"] = {
            "execution_context": execution_context.model_dump(mode="json"),
            **request_options.get("additional_body_parameters", {}),
        }

        try:
            deployment_id = str(self.deployment) if isinstance(self.deployment, UUID) else None
            deployment_name = self.deployment if isinstance(self.deployment, str) else None
        except AttributeError:
            raise NodeException(
                code=WorkflowErrorCode.NODE_EXECUTION,
                message="Expected subworkflow deployment attribute to be either a UUID or STR, got None instead",
            )

        try:
            subworkflow_stream = self._context.vellum_client.execute_workflow_stream(
                inputs=self._compile_subworkflow_inputs(),
                workflow_deployment_id=deployment_id,
                workflow_deployment_name=deployment_name,
                release_tag=self.release_tag,
                external_id=self.external_id,
                event_types=["WORKFLOW"],
                metadata=self.metadata,
                request_options=request_options,
            )
        except ApiError as e:
            self._handle_api_error(e)

        # We don't use the INITIATED event anyway, so we can just skip it
        # and use the exception handling to catch other api level errors
        try:
            next(subworkflow_stream)
        except ApiError as e:
            self._handle_api_error(e)

        outputs: Optional[List[WorkflowOutput]] = None
        fulfilled_output_names: Set[str] = set()
        for event in subworkflow_stream:
            if event.type != "WORKFLOW":
                continue
            if event.data.state == "INITIATED":
                continue
            elif event.data.state == "STREAMING":
                if event.data.output:
                    if event.data.output.state == "STREAMING":
                        yield BaseOutput(
                            name=event.data.output.name,
                            delta=event.data.output.delta,
                        )
                    elif event.data.output.state == "FULFILLED":
                        yield BaseOutput(
                            name=event.data.output.name,
                            value=event.data.output.value,
                        )
                        fulfilled_output_names.add(event.data.output.name)
            elif event.data.state == "FULFILLED":
                outputs = event.data.outputs
            elif event.data.state == "REJECTED":
                error = event.data.error
                if not error:
                    raise NodeException(
                        message="Expected to receive an error from REJECTED event",
                        code=WorkflowErrorCode.INTERNAL_ERROR,
                    )
                workflow_error = workflow_event_error_to_workflow_error(error)
                raise NodeException.of(workflow_error)

        if outputs is None:
            raise NodeException(
                message="Expected to receive outputs from Workflow Deployment",
                code=WorkflowErrorCode.INTERNAL_ERROR,
            )

        # For any outputs somehow in our final fulfilled outputs array,
        # but not fulfilled by the stream.
        for output in outputs:
            if output.name not in fulfilled_output_names:
                yield BaseOutput(
                    name=output.name,
                    value=output.value,
                )

    def _handle_api_error(self, e: ApiError):
        if e.status_code and e.status_code >= 400 and e.status_code < 500 and isinstance(e.body, dict):
            raise NodeException(
                message=e.body.get("detail", "Failed to execute Subworkflow Deployment"),
                code=WorkflowErrorCode.INVALID_INPUTS,
            ) from e

        raise NodeException(
            message="Failed to execute Subworkflow Deployment",
            code=WorkflowErrorCode.INTERNAL_ERROR,
        ) from e
