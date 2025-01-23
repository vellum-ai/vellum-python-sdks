from typing import Iterator

from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.displayable.bases import BasePromptDeploymentNode as BasePromptDeploymentNode
from vellum.workflows.outputs import BaseOutput
from vellum.workflows.types import MergeBehavior
from vellum.workflows.types.generics import StateType


class PromptDeploymentNode(BasePromptDeploymentNode[StateType]):
    """
    Used to execute a Prompt Deployment and surface a string output for convenience.

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
    """

    class Trigger(BasePromptDeploymentNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY

    class Outputs(BasePromptDeploymentNode.Outputs):
        """
        The outputs of the PromptDeploymentNode.

        text: str - The result of the Prompt Execution
        """

        text: str

    def run(self) -> Iterator[BaseOutput]:
        outputs = yield from self._process_prompt_event_stream()
        if not outputs:
            raise NodeException(
                message="Expected to receive outputs from Prompt",
                code=WorkflowErrorCode.INTERNAL_ERROR,
            )

        string_output = next((output for output in outputs if output.type == "STRING"), None)
        if not string_output or string_output.value is None:
            output_types = {output.type for output in outputs}
            is_plural = len(output_types) > 1
            raise NodeException(
                message=f"Expected to receive a non-null string output from Prompt. Only found outputs of type{'s' if is_plural else ''}: {', '.join(output_types)}",  # noqa: E501
                code=WorkflowErrorCode.INTERNAL_ERROR,
            )

        yield BaseOutput(name="text", value=string_output.value)
