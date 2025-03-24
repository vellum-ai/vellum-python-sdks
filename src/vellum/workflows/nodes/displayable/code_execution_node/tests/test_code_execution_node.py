import pytest
import os
from typing import Any, List, Union

from pydantic import BaseModel

from vellum import CodeExecutorResponse, NumberVellumValue, StringInput, StringVellumValue
from vellum.client.errors.bad_request_error import BadRequestError
from vellum.client.types.chat_message import ChatMessage
from vellum.client.types.code_execution_package import CodeExecutionPackage
from vellum.client.types.code_executor_secret_input import CodeExecutorSecretInput
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.number_input import NumberInput
from vellum.client.types.string_chat_message_content import StringChatMessageContent
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.displayable.code_execution_node import CodeExecutionNode
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum.workflows.state.base import BaseState, StateMeta
from vellum.workflows.types.core import Json


def test_run_node__happy_path(vellum_client):
    """Confirm that CodeExecutionNodes output the expected text and results when run."""

    # GIVEN a node that subclasses CodeExecutionNode
    class Inputs(BaseInputs):
        word: str

    class State(BaseState):
        pass

    fixture = os.path.abspath(os.path.join(__file__, "../fixtures/main.py"))

    class ExampleCodeExecutionNode(CodeExecutionNode[State, int]):
        filepath = fixture
        runtime = "PYTHON_3_11_6"
        packages = [
            CodeExecutionPackage(
                name="openai",
                version="1.0.0",
            )
        ]

        code_inputs = {
            "word": Inputs.word,
        }

    # AND we know what the Code Execution Node will respond with
    mock_code_execution = CodeExecutorResponse(
        log="hello",
        output=NumberVellumValue(value=5),
    )
    vellum_client.execute_code.return_value = mock_code_execution

    # WHEN we run the node
    node = ExampleCodeExecutionNode(
        state=State(
            meta=StateMeta(workflow_inputs=Inputs(word="hello")),
        )
    )
    outputs = node.run()

    # THEN the node should have produced the outputs we expect
    assert outputs == {"result": 5, "log": "hello"}

    # AND we should have invoked the Code with the expected inputs
    vellum_client.execute_code.assert_called_once_with(
        input_values=[
            StringInput(name="word", value="hello"),
        ],
        code="""\
def main(word: str) -> int:
    print(word)  # noqa: T201
    return len(word)
""",
        runtime="PYTHON_3_11_6",
        output_type="NUMBER",
        packages=[
            CodeExecutionPackage(
                name="openai",
                version="1.0.0",
            )
        ],
        request_options=None,
    )


def test_run_node__code_attribute(vellum_client):
    """Confirm that CodeExecutionNodes can use the `code` attribute to specify the code to execute."""

    # GIVEN a node that subclasses CodeExecutionNode
    class Inputs(BaseInputs):
        word: str

    class State(BaseState):
        pass

    class ExampleCodeExecutionNode(CodeExecutionNode[State, int]):
        code = """\
def main(word: str) -> int:
    print(word)  # noqa: T201
    return len(word)
"""
        runtime = "PYTHON_3_11_6"
        packages = [
            CodeExecutionPackage(
                name="openai",
                version="1.0.0",
            )
        ]

        code_inputs = {
            "word": Inputs.word,
        }

    # AND we know what the Code Execution Node will respond with
    mock_code_execution = CodeExecutorResponse(
        log="hello",
        output=NumberVellumValue(value=5),
    )
    vellum_client.execute_code.return_value = mock_code_execution

    # WHEN we run the node
    node = ExampleCodeExecutionNode(
        state=State(
            meta=StateMeta(workflow_inputs=Inputs(word="hello")),
        )
    )
    outputs = node.run()

    # THEN the node should have produced the outputs we expect
    assert outputs == {"result": 5, "log": "hello"}

    # AND we should have invoked the Code with the expected inputs
    vellum_client.execute_code.assert_called_once_with(
        input_values=[
            StringInput(name="word", value="hello"),
        ],
        code="""\
def main(word: str) -> int:
    print(word)  # noqa: T201
    return len(word)
""",
        runtime="PYTHON_3_11_6",
        output_type="NUMBER",
        packages=[
            CodeExecutionPackage(
                name="openai",
                version="1.0.0",
            )
        ],
        request_options=None,
    )


def test_run_node__code_and_filepath_defined(vellum_client):
    """Confirm that CodeExecutionNodes raise an error if both `code` and `filepath` are defined."""

    # GIVEN a node that subclasses CodeExecutionNode
    class Inputs(BaseInputs):
        word: str

    class State(BaseState):
        pass

    fixture = os.path.abspath(os.path.join(__file__, "../fixtures/main.py"))

    class ExampleCodeExecutionNode(CodeExecutionNode[State, int]):
        filepath = fixture
        code = """\
def main(word: str) -> int:
    print(word)  # noqa: T201
    return len(word)
"""
        runtime = "PYTHON_3_11_6"
        packages = [
            CodeExecutionPackage(
                name="openai",
                version="1.0.0",
            )
        ]

        code_inputs = {
            "word": Inputs.word,
        }

    # AND we know what the Code Execution Node will respond with
    mock_code_execution = CodeExecutorResponse(
        log="hello",
        output=NumberVellumValue(value=5),
    )
    vellum_client.execute_code.return_value = mock_code_execution

    # WHEN we run the node
    node = ExampleCodeExecutionNode(
        state=State(
            meta=StateMeta(workflow_inputs=Inputs(word="hello")),
        )
    )
    with pytest.raises(NodeException) as exc_info:
        node.run()

    # THEN the node should have produced the exception we expected
    assert exc_info.value.message == "Cannot specify both `code` and `filepath` for a CodeExecutionNode"


def test_run_node__code_and_filepath_not_defined(vellum_client):
    """Confirm that CodeExecutionNodes raise an error if neither `code` nor `filepath` are defined."""

    # GIVEN a node that subclasses CodeExecutionNode
    class Inputs(BaseInputs):
        word: str

    class State(BaseState):
        pass

    class ExampleCodeExecutionNode(CodeExecutionNode[State, int]):
        runtime = "PYTHON_3_11_6"
        packages = [
            CodeExecutionPackage(
                name="openai",
                version="1.0.0",
            )
        ]

        code_inputs = {
            "word": Inputs.word,
        }

    # AND we know what the Code Execution Node will respond with
    mock_code_execution = CodeExecutorResponse(
        log="hello",
        output=NumberVellumValue(value=5),
    )
    vellum_client.execute_code.return_value = mock_code_execution

    # WHEN we run the node
    node = ExampleCodeExecutionNode(
        state=State(
            meta=StateMeta(workflow_inputs=Inputs(word="hello")),
        )
    )
    with pytest.raises(NodeException) as exc_info:
        node.run()

    # THEN the node should have produced the exception we expected
    assert exc_info.value.message == "Must specify either `code` or `filepath` for a CodeExecutionNode"


def test_run_node__vellum_secret(vellum_client):
    """Confirm that CodeExecutionNodes can use Vellum Secrets"""

    # GIVEN a node that subclasses CodeExecutionNode that references a Vellum Secret
    class State(BaseState):
        pass

    fixture = os.path.abspath(os.path.join(__file__, "../fixtures/main.py"))

    class ExampleCodeExecutionNode(CodeExecutionNode[State, int]):
        filepath = fixture
        runtime = "PYTHON_3_11_6"
        packages = [
            CodeExecutionPackage(
                name="openai",
                version="1.0.0",
            )
        ]

        code_inputs = {
            "word": VellumSecretReference("OPENAI_API_KEY"),
        }

    # AND we know what the Code Execution Node will respond with
    mock_code_execution = CodeExecutorResponse(
        log="",
        output=NumberVellumValue(value=0),
    )
    vellum_client.execute_code.return_value = mock_code_execution

    # WHEN we run the node
    node = ExampleCodeExecutionNode(state=State())
    outputs = node.run()

    # THEN the node should have produced the outputs we expect
    assert outputs == {"result": 0, "log": ""}

    # AND we should have invoked the Code with the expected inputs
    vellum_client.execute_code.assert_called_once_with(
        input_values=[
            CodeExecutorSecretInput(
                name="word",
                value="OPENAI_API_KEY",
            )
        ],
        code="""\
def main(word: str) -> int:
    print(word)  # noqa: T201
    return len(word)
""",
        runtime="PYTHON_3_11_6",
        output_type="NUMBER",
        packages=[
            CodeExecutionPackage(
                name="openai",
                version="1.0.0",
            )
        ],
        request_options=None,
    )


def test_run_node__int_input(vellum_client):
    """Confirm that CodeExecutionNodes can use int's as inputs"""

    # GIVEN a node that subclasses CodeExecutionNode that references an int
    class State(BaseState):
        pass

    fixture = os.path.abspath(os.path.join(__file__, "../fixtures/main.py"))

    class ExampleCodeExecutionNode(CodeExecutionNode[State, int]):
        filepath = fixture
        runtime = "PYTHON_3_11_6"
        packages = [
            CodeExecutionPackage(
                name="openai",
                version="1.0.0",
            )
        ]

        code_inputs = {
            "counter": 1,
        }

    # AND we know what the Code Execution Node will respond with
    mock_code_execution = CodeExecutorResponse(
        log="",
        output=NumberVellumValue(value=0),
    )
    vellum_client.execute_code.return_value = mock_code_execution

    # WHEN we run the node
    node = ExampleCodeExecutionNode(state=State())
    outputs = node.run()

    # THEN the node should have produced the outputs we expect
    assert outputs == {"result": 0, "log": ""}

    # AND we should have invoked the Code with the correct inputs
    assert vellum_client.execute_code.call_args_list[0].kwargs["input_values"] == [
        NumberInput(
            name="counter",
            value=1.0,
        )
    ]


def test_run_node__run_inline(vellum_client):
    """Confirm that CodeExecutionNodes run the code inline instead of through Vellum under certain conditions."""

    # GIVEN a node that subclasses CodeExecutionNode
    class ExampleCodeExecutionNode(CodeExecutionNode[BaseState, int]):
        code = """\
def main(word: str) -> int:
    print(word)  # noqa: T201
    return len(word)
"""
        runtime = "PYTHON_3_11_6"

        code_inputs = {
            "word": "hello",
        }

    # WHEN we run the node
    node = ExampleCodeExecutionNode()
    outputs = node.run()

    # THEN the node should have produced the outputs we expect
    assert outputs == {"result": 5, "log": "hello\n"}

    # AND we should have not invoked the Code via Vellum
    vellum_client.execute_code.assert_not_called()


def test_run_node__run_inline__incorrect_output_type():
    """Confirm that CodeExecutionNodes raise an error if the output type is incorrect during inline execution."""

    # GIVEN a node that subclasses CodeExecutionNode that returns a string but is defined to return an int
    class ExampleCodeExecutionNode(CodeExecutionNode[BaseState, int]):
        code = """\
def main(word: str) -> int:
    return word
"""
        runtime = "PYTHON_3_11_6"

        code_inputs = {
            "word": "hello",
        }

    # WHEN we run the node
    node = ExampleCodeExecutionNode()
    with pytest.raises(NodeException) as exc_info:
        node.run()

    # THEN the node should have produced the exception we expected
    assert exc_info.value.message == "Expected an output of type 'int', but received 'str'"


def test_run_node__run_inline__valid_dict_to_pydantic():
    """Confirm that CodeExecutionNodes can convert a dict to a Pydantic model during inline execution."""

    # GIVEN a node that subclasses CodeExecutionNode that returns a dict matching a Pydantic model
    class ExampleCodeExecutionNode(CodeExecutionNode[BaseState, FunctionCall]):
        code = """\
def main(word: str) -> int:
    return {
        "name": word,
        "arguments": {},
    }
"""
        runtime = "PYTHON_3_11_6"

        code_inputs = {
            "word": "hello",
        }

    # WHEN we run the node
    node = ExampleCodeExecutionNode()
    outputs = node.run()

    # THEN the node should have produced the outputs we expect
    assert outputs == {"result": FunctionCall(name="hello", arguments={}), "log": ""}


def test_run_node__run_inline__invalid_dict_to_pydantic():
    """Confirm that CodeExecutionNodes raise an error if the Pydantic validation fails during inline execution."""

    # GIVEN a node that subclasses CodeExecutionNode that returns a dict not matching a Pydantic model
    class ExampleCodeExecutionNode(CodeExecutionNode[BaseState, FunctionCall]):
        code = """\
def main(word: str) -> int:
    return {
        "n": word,
        "a": {},
    }
"""
        runtime = "PYTHON_3_11_6"

        code_inputs = {
            "word": "hello",
        }

    # WHEN we run the node
    node = ExampleCodeExecutionNode()
    with pytest.raises(NodeException) as exc_info:
        node.run()

    # THEN the node should have produced the exception we expected
    assert exc_info.value.message == "Expected an output of type 'FunctionCall', but received 'dict'"


def test_run_node__run_inline__valid_dict_to_pydantic_any_type():
    """Confirm that CodeExecutionNodes can convert a dict to a Pydantic model during inline execution."""

    # GIVEN a node that subclasses CodeExecutionNode that returns a dict matching Any
    class ExampleCodeExecutionNode(CodeExecutionNode[BaseState, Any]):
        code = """\
def main(word: str) -> dict:
    return {
        "name": "word",
        "arguments": {},
    }
    """
        runtime = "PYTHON_3_11_6"

        code_inputs = {
            "word": "hello",
        }

    # WHEN we run the node
    node = ExampleCodeExecutionNode()
    outputs = node.run()

    # THEN the node should have produced the outputs we expect
    assert outputs == {
        "result": {
            "name": "word",
            "arguments": {},
        },
        "log": "",
    }


def test_run_node__array_input_with_vellum_values(vellum_client):
    """Confirm that CodeExecutionNodes can handle arrays containing VellumValue objects."""

    # GIVEN a node that subclasses CodeExecutionNode that processes an array of VellumValues
    class State(BaseState):
        pass

    class ExampleCodeExecutionNode(CodeExecutionNode[State, str]):
        code = """\
from typing import List, Dict
def main(arg1: List[Dict]) -> str:
    return arg1[0]["value"] + " " + arg1[1]["value"]
"""
        runtime = "PYTHON_3_11_6"

        code_inputs = {
            "arg1": [
                StringVellumValue(type="STRING", value="Hello", name="First"),
                StringVellumValue(type="STRING", value="World", name="Second"),
            ],
        }

    # WHEN we run the node
    node = ExampleCodeExecutionNode(state=State())
    outputs = node.run()

    # THEN the node should successfully concatenate the values
    assert outputs == {"result": "Hello World", "log": ""}

    # AND we should not have invoked the Code via Vellum since it's running inline
    vellum_client.execute_code.assert_not_called()


def test_run_node__union_output_type(vellum_client):
    """Confirm that CodeExecutionNodes can handle Union output types."""

    # GIVEN a node that subclasses CodeExecutionNode that returns a Union type
    class State(BaseState):
        pass

    class ExampleCodeExecutionNode(CodeExecutionNode[State, Union[float, int]]):
        code = """\
from typing import List, Dict
def main(arg1: List[Dict]) -> float:
    return arg1[0]["value"] + arg1[1]["value"]
"""
        runtime = "PYTHON_3_11_6"

        code_inputs = {
            "arg1": [
                NumberVellumValue(type="NUMBER", value=1.0, name="First"),
                NumberVellumValue(type="NUMBER", value=2.0, name="Second"),
            ],
        }

    # WHEN we run the node
    node = ExampleCodeExecutionNode(state=State())
    outputs = node.run()

    # THEN the node should successfully sum the values
    assert outputs == {"result": 3.0, "log": ""}

    # AND we should not have invoked the Code via Vellum since it's running inline
    vellum_client.execute_code.assert_not_called()


def test_run_node__code_execution_error():
    # GIVEN a node that will raise an error during execution
    class State(BaseState):
        pass

    class ExampleCodeExecutionNode(CodeExecutionNode[State, int]):
        code = """\
def main(arg1: int, arg2: int) -> int:
    return arg1 + arg2 + arg3
"""
        runtime = "PYTHON_3_11_6"
        code_inputs = {
            "arg1": 1,
            "arg2": 2,
        }

    # WHEN we run the node
    node = ExampleCodeExecutionNode(state=State())

    # THEN it should raise a NodeException with the execution error
    with pytest.raises(NodeException) as exc_info:
        node.run()

    # AND the error should contain the execution error details
    assert "name 'arg3' is not defined" in str(exc_info.value)
    assert exc_info.value.code == WorkflowErrorCode.INVALID_CODE


def test_run_node__array_of_bools_input():
    # GIVEN a node that will raise an error during execution
    class ExampleCodeExecutionNode(CodeExecutionNode[BaseState, int]):
        code = """\
def main(arg1: list[bool]) -> int:
    return len(arg1)
"""
        runtime = "PYTHON_3_11_6"
        code_inputs = {
            "arg1": [True, False, True],
        }

    # WHEN we run the node
    node = ExampleCodeExecutionNode()

    # THEN it should raise a NodeException with the execution error
    outputs = node.run()

    # AND the error should contain the execution error details
    assert outputs == {"result": 3, "log": ""}


def test_run_node__union_output_type__pydantic_children():
    # GIVEN a node that is a union type with a pydantic child
    class OptionOne(BaseModel):
        foo: str

    class OptionTwo(BaseModel):
        bar: int

    class ExampleCodeExecutionNode(CodeExecutionNode[BaseState, Union[OptionOne, OptionTwo]]):
        code = """\
def main():
    return { "foo": "hello" }
"""
        runtime = "PYTHON_3_11_6"
        code_inputs = {}

    # WHEN we run the node
    node = ExampleCodeExecutionNode()

    # THEN it should run successfully
    outputs = node.run()

    # AND the result should be the correct type
    assert outputs == {"result": OptionOne(foo="hello"), "log": ""}


def test_run_node__union_output_type__miss():
    # GIVEN a node that is a union type
    class ExampleCodeExecutionNode(CodeExecutionNode[BaseState, Union[int, float]]):
        code = """\
def main():
    return "hello"
"""
        runtime = "PYTHON_3_11_6"
        code_inputs = {}

    # WHEN we run the node
    node = ExampleCodeExecutionNode()

    # THEN it should raise a NodeException with the execution error
    with pytest.raises(NodeException) as exc_info:
        node.run()

    # AND the error should contain the execution error details
    assert exc_info.value.message == "Expected an output of type 'int | float', but received 'str'"


def test_run_node__chat_history_output_type():
    # GIVEN a node that that has a chat history return type
    class ExampleCodeExecutionNode(CodeExecutionNode[BaseState, List[ChatMessage]]):
        code = """\
def main():
    return [
        {
            "role": "USER",
            "content": {
                "type": "STRING",
                "value": "Hello, world!",
            }
        }
    ]
"""
        code_inputs = {}
        runtime = "PYTHON_3_11_6"

    # WHEN we run the node
    node = ExampleCodeExecutionNode()
    outputs = node.run()

    # AND the error should contain the execution error details
    assert outputs == {
        "result": [ChatMessage(role="USER", content=StringChatMessageContent(value="Hello, world!"))],
        "log": "",
    }


def test_run_node__execute_code_api_fails__node_exception(vellum_client):
    # GIVEN a node that will throw a JSON.parse error
    class ExampleCodeExecutionNode(CodeExecutionNode[BaseState, Json]):
        code = """\
async function main(inputs: {
  data: string,
}): Promise<string> {
  return JSON.parse(inputs.data)
}
"""
        code_inputs = {
            "data": "not a valid json string",
        }
        runtime = "TYPESCRIPT_5_3_3"

    # AND the execute_code API will fail
    message = """\
Code execution error (exit code 1): undefined:1
not a valid json string
 ^

SyntaxError: Unexpected token 'o', \"not a valid\"... is not valid JSON
    at JSON.parse (<anonymous>)
    at Object.eval (eval at execute (/workdir/runner.js:16:18), <anonymous>:40:40)
    at step (eval at execute (/workdir/runner.js:16:18), <anonymous>:32:23)
    at Object.eval [as next] (eval at execute (/workdir/runner.js:16:18), <anonymous>:13:53)
    at eval (eval at execute (/workdir/runner.js:16:18), <anonymous>:7:71)
    at new Promise (<anonymous>)
    at __awaiter (eval at execute (/workdir/runner.js:16:18), <anonymous>:3:12)
    at Object.main (eval at execute (/workdir/runner.js:16:18), <anonymous>:38:12)
    at execute (/workdir/runner.js:17:33)
    at Interface.<anonymous> (/workdir/runner.js:58:5)

Node.js v21.7.3
"""
    vellum_client.execute_code.side_effect = BadRequestError(
        body={
            "message": message,
            "log": "",
        }
    )

    # WHEN we run the node
    node = ExampleCodeExecutionNode()
    with pytest.raises(NodeException) as exc_info:
        node.run()

    # AND the error should contain the execution error details
    assert exc_info.value.message == message


def test_run_node__execute_code__list_extends():
    # GIVEN a node that will return a list with output type Json
    class ExampleCodeExecutionNode(CodeExecutionNode[BaseState, Json]):
        code = """\
def main(left, right):
    all = []
    all.extend(left)
    all.extend(right)
    return all
"""
        code_inputs = {
            "left": [1, 2, 3],
            "right": [4, 5, 6],
        }
        runtime = "PYTHON_3_11_6"

    # WHEN we run the node
    node = ExampleCodeExecutionNode()
    outputs = node.run()

    # AND the result should be the correct output
    assert outputs == {"result": [1, 2, 3, 4, 5, 6], "log": ""}


def test_run_node__execute_code__non_str_print():
    # GIVEN a node that will print a non-string value
    class ExampleCodeExecutionNode(CodeExecutionNode[BaseState, str]):
        code = """\
def main():
    print(type(1))
    return "hello"
"""
        code_inputs = {}
        runtime = "PYTHON_3_11_6"

    # WHEN we run the node
    node = ExampleCodeExecutionNode()
    outputs = node.run()

    # AND the result should be the correct output
    assert outputs == {"result": "hello", "log": "<class 'int'>\n"}


def test_run_node__execute_code__invalid_key_access():
    # GIVEN a node that will access an invalid key
    class ExampleCodeExecutionNode(CodeExecutionNode[BaseState, str]):
        code = """\
def main(arg1: list) -> str:
    return arg1["invalid"]
"""
        code_inputs = {
            "arg1": {"foo": "bar"},
        }
        runtime = "PYTHON_3_11_6"

    # WHEN we run the node
    with pytest.raises(NodeException) as exc_info:
        node = ExampleCodeExecutionNode()
        node.run()

    # AND the result should be the correct output
    assert exc_info.value.message == "dict has no key: 'invalid'"


def test_run_node__execute_code__value_key_access():
    # GIVEN a node that will access the value key before the nested key
    class ExampleCodeExecutionNode(CodeExecutionNode[BaseState, str]):
        code = """\
def main(arg1: list) -> str:
    return arg1["value"]["foo"]
"""
        code_inputs = {
            "arg1": {"foo": "bar"},
        }
        runtime = "PYTHON_3_11_6"

    # WHEN we run the node
    node = ExampleCodeExecutionNode()
    outputs = node.run()

    # AND the result should be the correct output
    assert outputs == {"result": "bar", "log": ""}
