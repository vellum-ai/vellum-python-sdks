import json
from uuid import uuid4
from typing import Any, Iterator

import boto3

from vellum import (
    AdHocExecutePromptEvent,
    FulfilledAdHocExecutePromptEvent,
    InitiatedAdHocExecutePromptEvent,
    PromptOutput,
    StringVellumValue,
)
from vellum.prompts.blocks.compilation import compile_prompt_blocks
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.displayable import InlinePromptNode


class LocalBedrockNode(InlinePromptNode):
    """
    Used to execute a Prompt against the AWS Bedrock API directly instead of growing through Vellum.
    """

    # Override
    def _get_prompt_event_stream(self) -> Iterator[AdHocExecutePromptEvent]:
        """
        This is the main method that needs to be overridden to execute the prompt against the Bedrock API directly.
        """

        client = self._get_client()

        execution_id = str(uuid4())

        yield InitiatedAdHocExecutePromptEvent(
            execution_id=execution_id,
        )

        response = client.invoke_model(
            modelId=".".join(self.ml_model.replace("aws-bedrock//", "").split("/")[0:-1]),
            body=json.dumps(self._get_body()),
        )
        response_body = json.loads(response["body"].read())

        content = response_body.get("content")
        outputs: list[PromptOutput] = []
        for part in content:
            if part.get("type") == "text":
                outputs.append(StringVellumValue(value=part["text"]))

        yield FulfilledAdHocExecutePromptEvent(
            outputs=outputs,
            execution_id=execution_id,
        )

    def _get_client(self) -> Any:
        return boto3.client("bedrock-runtime", region_name="us-west-2")

    def _get_body(self) -> dict:
        input_variables, input_values = self._compile_prompt_inputs()
        compiled_blocks = compile_prompt_blocks(
            blocks=self.blocks, inputs=input_values, input_variables=input_variables
        )

        system_blocks: list[dict] = []
        messages: list[dict] = []

        for block in compiled_blocks:
            if block.block_type != "CHAT_MESSAGE":
                continue

            contents: list[dict[str, Any]] = []
            for child_block in block.blocks:
                if child_block.content.type == "STRING":
                    text = child_block.content.value
                    if text.strip():
                        contents.append({"type": "text", "text": text})
                elif child_block.content.type == "JSON":
                    contents.append(
                        {
                            "type": "text",
                            "text": json.dumps(child_block.content.value),
                        }
                    )
                else:
                    raise NodeException(f"Unsupported child block type: {child_block.content.type}")

            if block.role == "SYSTEM":
                system_blocks = contents

            elif block.role == "USER":
                messages.append({"role": "user", "content": contents})

            elif block.role == "ASSISTANT":
                messages.append({"role": "assistant", "content": contents})

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": messages,
            "max_tokens": self.parameters.max_tokens,
            "temperature": self.parameters.temperature,
        }

        if system_blocks:
            body["system"] = system_blocks

        return body
