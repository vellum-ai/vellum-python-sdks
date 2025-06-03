import json
from typing import Any, Dict, Iterator, Type, Union

from vellum.workflows.constants import undefined
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.displayable.bases import BaseInlinePromptNode as BaseInlinePromptNode
from vellum.workflows.outputs import BaseOutput
from vellum.workflows.types import MergeBehavior
from vellum.workflows.types.generics import StateType


class InlinePromptNode(BaseInlinePromptNode[StateType]):
    """
    Used to execute a Prompt defined inline.

    prompt_inputs: EntityInputsInterface - The inputs for the Prompt
    ml_model: str - Either the ML Model's UUID or its name.
    blocks: List[PromptBlock] - The blocks that make up the Prompt
    functions: Optional[List[FunctionDefinition]] - The functions to include in the Prompt
    parameters: PromptParameters - The parameters for the Prompt
    expand_meta: Optional[AdHocExpandMeta] - Expandable execution fields to include in the response
    request_options: Optional[RequestOptions] - The request options to use for the Prompt Execution
    """

    class Trigger(BaseInlinePromptNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY

    class Outputs(BaseInlinePromptNode.Outputs):
        """
        The outputs of the InlinePromptNode.

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
                json_output = output.value
            elif output.type == "FUNCTION_CALL":
                string_outputs.append(output.value.model_dump_json(indent=4))
            else:
                string_outputs.append(output.value.message)

        value = "\n".join(string_outputs)
        yield BaseOutput(name="text", value=value)

        if json_output:
            yield BaseOutput(name="json", value=json_output)
