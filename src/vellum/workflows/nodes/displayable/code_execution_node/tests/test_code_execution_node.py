import pytest
import os

from vellum import CodeExecutorResponse, NumberVellumValue, StringInput
from vellum.client.types.code_execution_package import CodeExecutionPackage
from vellum.client.types.code_executor_secret_input import CodeExecutorSecretInput
from vellum.client.types.function_call import FunctionCall
from vellum.workflows.exceptions import NodeException
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.displayable.code_execution_node import CodeExecutionNode
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum.workflows.state.base import BaseState, StateMeta


def test_run_workflow__happy_path(vellum_client):
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


def test_run_workflow__code_attribute(vellum_client):
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


def test_run_workflow__code_and_filepath_defined(vellum_client):
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


def test_run_workflow__code_and_filepath_not_defined(vellum_client):
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


def test_run_workflow__vellum_secret(vellum_client):
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


def test_run_workflow__run_inline(vellum_client):
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


def test_run_workflow__run_inline__incorrect_output_type():
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


def test_run_workflow__run_inline__valid_dict_to_pydantic():
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


def test_run_workflow__run_inline__invalid_dict_to_pydantic():
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
    assert (
        exc_info.value.message
        == """\
2 validation errors for FunctionCall
arguments
  Field required [type=missing, input_value={'n': 'hello', 'a': {}}, input_type=dict]
name
  Field required [type=missing, input_value={'n': 'hello', 'a': {}}, input_type=dict]\
"""
    )
