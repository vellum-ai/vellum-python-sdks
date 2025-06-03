import json
from typing import Any, Dict, Iterator, Type, Union

from vellum.workflows.constants import undefined
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.displayable.bases import BasePromptDeploymentNode as BasePromptDeploymentNode
from vellum.workflows.outputs import BaseOutput
from vellum.workflows.types import MergeBehavior
from vellum.workflows.types.generics import StateType


class PromptDeploymentNode(BasePromptDeploymentNode[StateType]):
    """
    Used to execute a Prompt Deployment and surface a string output and json output if applicable for convenience.

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
        json: Optional[Dict[Any, Any]] - The result of the Prompt Execution in JSON format
        """

        text: str
        json: Union[Dict[Any, Any], Type[undefined]] = undefined

    def run(self) -> Iterator[BaseOutput]:
        outputs = yield from self._process_prompt_event_stream()
        if not outputs:
            raise NodeException(
                message="Expected to receive outputs from Prompt",
                code=WorkflowErrorCode.INTERNAL_ERROR,
            )

        string_outputs = []
        json_output = None

        for output in outputs:
            if output.value is None:
                continue

            if output.type == "STRING":
                string_outputs.append(output.value)
                try:
                    json_output = json.loads(output.value)
                except (json.JSONDecodeError, TypeError):
                    pass
            elif output.type == "JSON":
                string_outputs.append(json.dumps(output.value, indent=4))
            elif output.type == "FUNCTION_CALL":
                string_outputs.append(output.value.model_dump_json(indent=4))
            else:
                string_outputs.append(output.value.message)

        value = "\n".join(string_outputs)
        yield BaseOutput(name="text", value=value)

        if json_output:
            yield BaseOutput(name="json", value=json_output)
