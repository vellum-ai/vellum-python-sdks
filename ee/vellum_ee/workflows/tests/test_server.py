import pytest
import sys
from uuid import uuid4
from typing import Type, cast

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.client.types.code_executor_response import CodeExecutorResponse
from vellum.client.types.number_vellum_value import NumberVellumValue
from vellum.workflows import BaseWorkflow
from vellum.workflows.exceptions import WorkflowInitializationException
from vellum.workflows.nodes import BaseNode
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.utils.uuids import generate_workflow_deployment_prefix
from vellum.workflows.utils.zip import zip_file_map
from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay
from vellum_ee.workflows.server.virtual_file_loader import VirtualFileFinder


def test_load_workflow_event_display_context():
    from vellum.workflows.events.workflow import WorkflowEventDisplayContext

    # We are actually just ensuring there are no circular dependencies when
    # our Workflow Server imports this class.
    assert issubclass(WorkflowEventDisplayContext, UniversalBaseModel)


def test_load_from_module__lazy_reference_in_file_loader():
    # GIVEN a workflow module with a node containing a lazy reference
    files = {
        "__init__.py": "",
        "workflow.py": """\
from vellum.workflows import BaseWorkflow
from .nodes.start_node import StartNode

class Workflow(BaseWorkflow):
    graph = StartNode
""",
        "nodes/__init__.py": """\
from .start_node import StartNode

__all__ = [
    "StartNode",
]
""",
        "nodes/start_node.py": """\
from vellum.workflows.nodes import BaseNode
from vellum.workflows.references import LazyReference

class StartNode(BaseNode):
    foo = LazyReference(lambda: StartNode.Outputs.bar)

    class Outputs(BaseNode.Outputs):
        bar = str
""",
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    sys.meta_path.append(VirtualFileFinder(files, namespace))

    # WHEN the workflow is loaded
    Workflow = BaseWorkflow.load_from_module(namespace)
    workflow = Workflow()

    # THEN the workflow is successfully initialized
    assert workflow

    # AND the graph is just a BaseNode
    # ideally this would be true, but the loader uses a different BaseNode class definition than
    # the one in this test module.
    # assert isinstance(workflow.graph, BaseNode)
    start_node = cast(Type[BaseNode], workflow.graph)
    assert start_node.__bases__ == (BaseNode,)

    # AND the lazy reference has the correct name
    assert start_node.foo.instance
    assert start_node.foo.instance.name == "StartNode.Outputs.bar"


def test_load_from_module__ts_code_in_file_loader(
    vellum_client,
):
    # GIVEN typescript code
    ts_code = """async function main(): any {
  return 5;
}"""

    # AND a workflow module with only a code execution node
    files = {
        "__init__.py": "",
        "workflow.py": """
from vellum.workflows import BaseWorkflow
from .nodes.code_execution_node import CodeExecutionNode

class Workflow(BaseWorkflow):
    graph = CodeExecutionNode

    class Outputs(BaseWorkflow.Outputs):
       final_output = CodeExecutionNode.Outputs.result
""",
        "nodes/__init__.py": """
from .code_execution_node import CodeExecutionNode

__all__ = ["CodeExecutionNode"]
""",
        "nodes/code_execution_node/__init__.py": """
from typing import Any

from vellum.workflows.nodes.displayable import CodeExecutionNode as BaseCodeExecutionNode
from vellum.workflows.state import BaseState

class CodeExecutionNode(BaseCodeExecutionNode[BaseState, int]):
    filepath = "./script.ts"
    code_inputs = {}
    runtime = "TYPESCRIPT_5_3_3"
    packages = []
""",
        "nodes/code_execution_node/script.ts": ts_code,
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    finder = VirtualFileFinder(files, namespace)
    sys.meta_path.append(finder)

    # AND we know what the Code Execution Node will respond with
    mock_code_execution = CodeExecutorResponse(
        log="hello",
        output=NumberVellumValue(value=5),
    )
    vellum_client.execute_code.return_value = mock_code_execution

    # WHEN the workflow is loaded
    Workflow = BaseWorkflow.load_from_module(namespace)
    workflow = Workflow(context=WorkflowContext(generated_files=files))

    # THEN the workflow is successfully initialized
    assert workflow

    event = workflow.run()
    assert event.name == "workflow.execution.fulfilled"

    # AND we get the code execution result
    assert event.body.outputs == {"final_output": 5.0}

    # AND the workflow definition module is correctly serialized as a list
    serialized_event = event.model_dump(mode="json")
    workflow_definition = serialized_event["body"]["workflow_definition"]
    assert workflow_definition["module"] == [namespace, "workflow"]


def test_load_from_module__simple_code_execution_node_with_try(
    vellum_client,
):
    # GIVEN a simple Python script
    py_code = """def main() -> int:
    print("Hello")
    return 1
"""

    # AND a workflow module with only a code execution node
    files = {
        "__init__.py": "",
        "workflow.py": """
from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .nodes.code_execution_node import CodeExecutionNode

class Workflow(BaseWorkflow):
    graph = CodeExecutionNode

    class Outputs(BaseWorkflow.Outputs):
       final_output = CodeExecutionNode.Outputs.result
""",
        "nodes/__init__.py": """
from .code_execution_node import CodeExecutionNode

__all__ = ["CodeExecutionNode"]
""",
        "nodes/code_execution_node/__init__.py": """
from typing import Union

from vellum.workflows.nodes.core import TryNode
from vellum.workflows.nodes.displayable import CodeExecutionNode as BaseCodeExecutionNode
from vellum.workflows.state import BaseState

@TryNode.wrap()
class CodeExecutionNode(BaseCodeExecutionNode[BaseState, Union[float, int]]):
    filepath = "./script.py"
    code_inputs = {}
    runtime = "PYTHON_3_11_6"
    packages = []
""",
        "nodes/code_execution_node/script.py": py_code,
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    finder = VirtualFileFinder(files, namespace)
    sys.meta_path.append(finder)

    # AND we know what the Code Execution Node will respond with
    mock_code_execution = CodeExecutorResponse(
        log="hello",
        output=NumberVellumValue(value=1),
    )
    vellum_client.execute_code.return_value = mock_code_execution

    # WHEN the workflow is loaded
    Workflow = BaseWorkflow.load_from_module(namespace)
    workflow = Workflow(context=WorkflowContext(generated_files=files))

    # THEN the workflow is successfully initialized
    assert workflow

    # WHEN we run the workflow
    event = workflow.run()

    # THEN the execution is fulfilled
    assert event.name == "workflow.execution.fulfilled"

    # AND we get the code execution result
    assert event.body.outputs == {"final_output": 1.0}


def test_load_from_module__simple_code_execution_node_with_retry(
    vellum_client,
):
    # GIVEN a simple Python script
    py_code = """def main() -> int:
    print("Hello")
    return 1
"""

    # AND a workflow module with only a code execution node wrapped with RetryNode
    files = {
        "__init__.py": "",
        "workflow.py": """
from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .nodes.code_execution_node import CodeExecutionNode

class Workflow(BaseWorkflow):
    graph = CodeExecutionNode

    class Outputs(BaseWorkflow.Outputs):
       final_output = CodeExecutionNode.Outputs.result
""",
        "nodes/__init__.py": """
from .code_execution_node import CodeExecutionNode

__all__ = ["CodeExecutionNode"]
""",
        "nodes/code_execution_node/__init__.py": """
from typing import Union

from vellum.workflows.nodes.core.retry_node.node import RetryNode
from vellum.workflows.nodes.displayable import CodeExecutionNode as BaseCodeExecutionNode
from vellum.workflows.state import BaseState

@RetryNode.wrap(max_attempts=3)
class CodeExecutionNode(BaseCodeExecutionNode[BaseState, Union[float, int]]):
    filepath = "./script.py"
    code_inputs = {}
    runtime = "PYTHON_3_11_6"
    packages = []
""",
        "nodes/code_execution_node/script.py": py_code,
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    finder = VirtualFileFinder(files, namespace)
    sys.meta_path.append(finder)

    # AND we know what the Code Execution Node will respond with
    mock_code_execution = CodeExecutorResponse(
        log="hello",
        output=NumberVellumValue(value=1),
    )
    vellum_client.execute_code.return_value = mock_code_execution

    # WHEN the workflow is loaded
    Workflow = BaseWorkflow.load_from_module(namespace)
    workflow = Workflow(context=WorkflowContext(generated_files=files))

    # THEN the workflow is successfully initialized
    assert workflow

    # WHEN we run the workflow
    event = workflow.run()

    # THEN the execution is fulfilled
    assert event.name == "workflow.execution.fulfilled"

    # AND we get the code execution result
    assert event.body.outputs == {"final_output": 1.0}


def test_load_from_module__code_execution_within_subworkflow(
    vellum_client,
):
    # GIVEN a simple Python script
    py_code = """def main() -> int:
    print("Hello")
    return 1
"""

    # AND a workflow module with a subworkflow containing a code execution node
    files = {
        "__init__.py": "",
        "workflow.py": """
from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .nodes.subworkflow import Subworkflow

class Workflow(BaseWorkflow):
    graph = Subworkflow

    class Outputs(BaseWorkflow.Outputs):
       final_output = Subworkflow.Outputs.result
""",
        "nodes/__init__.py": """
from .subworkflow import Subworkflow

__all__ = ["Subworkflow"]
""",
        "nodes/subworkflow/__init__.py": """
from vellum.workflows.nodes.displayable import InlineSubworkflowNode

from .workflow import SubworkflowWorkflow

class Subworkflow(InlineSubworkflowNode):
    subworkflow = SubworkflowWorkflow
""",
        "nodes/subworkflow/nodes/__init__.py": """
from .code_execution_node import CodeExecutionNode

__all__ = ["CodeExecutionNode"]
""",
        "nodes/subworkflow/nodes/code_execution_node/__init__.py": """
from typing import Union

from vellum.workflows.nodes.displayable import CodeExecutionNode as BaseCodeExecutionNode
from vellum.workflows.state import BaseState

class CodeExecutionNode(BaseCodeExecutionNode[BaseState, Union[float, int]]):
    filepath = "./script.py"
    code_inputs = {}
    runtime = "PYTHON_3_11_6"
    packages = []
""",
        "nodes/subworkflow/nodes/code_execution_node/script.py": py_code,
        "nodes/subworkflow/workflow.py": """
from vellum.workflows import BaseWorkflow

from .nodes.code_execution_node import CodeExecutionNode

class SubworkflowWorkflow(BaseWorkflow):
    graph = CodeExecutionNode

    class Outputs(BaseWorkflow.Outputs):
        result = CodeExecutionNode.Outputs.result
""",
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    finder = VirtualFileFinder(files, namespace)
    sys.meta_path.append(finder)

    # AND we know what the Code Execution Node will respond with
    mock_code_execution = CodeExecutorResponse(
        log="hello",
        output=NumberVellumValue(value=1),
    )
    vellum_client.execute_code.return_value = mock_code_execution

    # WHEN the workflow is loaded
    Workflow = BaseWorkflow.load_from_module(namespace)
    workflow = Workflow(context=WorkflowContext(generated_files=files))

    # THEN the workflow is successfully initialized
    assert workflow

    # WHEN we run the workflow
    event = workflow.run()

    # THEN the execution is fulfilled
    assert event.name == "workflow.execution.fulfilled"

    # AND we get the code execution result from the subworkflow
    assert event.body.outputs == {"final_output": 1.0}


def test_load_from_module__code_execution_within_map_node(
    vellum_client,
):
    # GIVEN a simple Python script
    py_code = """def main() -> int:
    print("Hello")
    return 1
"""

    # AND a workflow module with a map node containing a code execution node
    files = {
        "__init__.py": "",
        "workflow.py": """
from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .nodes.map_node import MapNode

class Workflow(BaseWorkflow):
    graph = MapNode
    
    class Outputs(BaseWorkflow.Outputs):  # noqa: W293
       results = MapNode.Outputs.final_output
""",
        "nodes/__init__.py": """
from .map_node import MapNode

__all__ = ["MapNode"]
""",
        "nodes/map_node/__init__.py": """
from vellum.workflows.nodes.core.map_node import MapNode as BaseMapNode

from .workflow import MapNodeWorkflow

class MapNode(BaseMapNode):
    items = ["foo", "bar", "baz"]
    subworkflow = MapNodeWorkflow
    max_concurrency = 4
""",
        "nodes/map_node/nodes/__init__.py": """
from .code_execution_node import CodeExecutionNode

__all__ = ["CodeExecutionNode"]
""",
        "nodes/map_node/nodes/code_execution_node/__init__.py": """
from typing import Union

from vellum.workflows.nodes.displayable import CodeExecutionNode as BaseCodeExecutionNode
from vellum.workflows.state import BaseState

class CodeExecutionNode(BaseCodeExecutionNode[BaseState, Union[float, int]]):
    filepath = "./script.py"
    code_inputs = {}
    runtime = "PYTHON_3_11_6"
    packages = []
""",
        "nodes/map_node/nodes/code_execution_node/script.py": py_code,
        "nodes/map_node/workflow.py": """
from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .nodes.code_execution_node import CodeExecutionNode

class MapNodeInputs:
    item: str
    index: int

class MapNodeWorkflow(BaseWorkflow):
    graph = CodeExecutionNode
    
    class Outputs(BaseWorkflow.Outputs):  # noqa: W293
        final_output = CodeExecutionNode.Outputs.result
""",
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    finder = VirtualFileFinder(files, namespace)
    sys.meta_path.append(finder)

    # AND we know what the Code Execution Node will respond with
    mock_code_execution = CodeExecutorResponse(
        log="hello",
        output=NumberVellumValue(value=3),
    )
    vellum_client.execute_code.return_value = mock_code_execution

    # WHEN the workflow is loaded
    Workflow = BaseWorkflow.load_from_module(namespace)
    workflow = Workflow(context=WorkflowContext(generated_files=files))

    # THEN the workflow is successfully initialized
    assert workflow

    # WHEN we run the workflow
    event = workflow.run()

    # THEN the execution is fulfilled
    assert event.name == "workflow.execution.fulfilled"

    # AND we get the map node results as a list
    assert event.body.outputs == {"results": [1.0, 1.0, 1.0]}


def test_load_from_module__syntax_error_in_node_file():
    """
    Tests that a syntax error in a node file raises WorkflowInitializationException with user-facing message.
    """
    # GIVEN a workflow module with a node file containing a syntax error (missing colon)
    files = {
        "__init__.py": "",
        "workflow.py": """\
from vellum.workflows import BaseWorkflow
from .nodes.broken_node import BrokenNode

class Workflow(BaseWorkflow):
    graph = BrokenNode
""",
        "nodes/__init__.py": "",
        "nodes/broken_node.py": """\
from vellum.workflows.nodes import BaseNode

class BrokenNode(BaseNode)  # Missing colon
    \"\"\"This node has a syntax error.\"\"\"
""",
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    sys.meta_path.append(VirtualFileFinder(files, namespace))

    # WHEN we attempt to load the workflow
    # THEN it should raise WorkflowInitializationException
    with pytest.raises(WorkflowInitializationException) as exc_info:
        BaseWorkflow.load_from_module(namespace)

    # AND the error message should be user-friendly
    error_message = str(exc_info.value)
    assert "Syntax Error raised while loading Workflow:" in error_message
    assert "invalid syntax" in error_message or "expected ':'" in error_message


def test_load_from_module__name_error_in_node_file():
    """
    Tests that a NameError in a node file raises WorkflowInitializationException with user-facing message.
    """
    # GIVEN a workflow module with a node file containing a NameError (undefined class reference)
    files = {
        "__init__.py": "",
        "workflow.py": """\
from vellum.workflows import BaseWorkflow
from .nodes.broken_node import BrokenNode

class Workflow(BaseWorkflow):
    graph = BrokenNode
""",
        "nodes/__init__.py": "",
        "nodes/broken_node.py": """\
from vellum.workflows.nodes import BaseNode

class BrokenNode(BaseNode):
    some_attribute = UndefinedClass()
""",
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    sys.meta_path.append(VirtualFileFinder(files, namespace))

    # WHEN we attempt to load the workflow
    # THEN it should raise WorkflowInitializationException
    with pytest.raises(WorkflowInitializationException) as exc_info:
        BaseWorkflow.load_from_module(namespace)

    # AND the error message should be user-friendly
    error_message = str(exc_info.value)
    assert "Invalid variable reference:" in error_message
    assert "UndefinedClass" in error_message or "not defined" in error_message


def test_load_from_module__module_not_found_error():
    """
    Tests that a ModuleNotFoundError raises WorkflowInitializationException with user-facing message.
    """
    # GIVEN a workflow module that imports a non-existent module
    files = {
        "__init__.py": "",
        "workflow.py": """\
from vellum.workflows import BaseWorkflow
from .non_existent_module import SomeClass

class Workflow(BaseWorkflow):
    graph = None
""",
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    sys.meta_path.append(VirtualFileFinder(files, namespace, source_module="test"))

    # WHEN we attempt to load the workflow
    # THEN it should raise WorkflowInitializationException
    with pytest.raises(WorkflowInitializationException) as exc_info:
        BaseWorkflow.load_from_module(namespace)

    # AND the error message should be user-friendly and show source_module instead of namespace
    error_message = str(exc_info.value)
    assert error_message == "Workflow module not found: No module named 'test.non_existent_module'"


def test_load_from_module__module_not_found_error_with_external_package():
    """
    Tests that when ModuleNotFoundError occurs for an external package (not containing the namespace),
    the exception includes vellum_on_error_action set to CREATE_CUSTOM_IMAGE in raw_data.
    """

    # GIVEN a workflow module that imports a non-existent external package
    files = {
        "__init__.py": "",
        "workflow.py": """\
from vellum.workflows import BaseWorkflow
import some_external_package

class Workflow(BaseWorkflow):
    graph = None
""",
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    finder = VirtualFileFinder(files, namespace, source_module="test")
    sys.meta_path.append(finder)

    # WHEN we attempt to load the workflow
    # THEN it should raise WorkflowInitializationException
    with pytest.raises(WorkflowInitializationException) as exc_info:
        BaseWorkflow.load_from_module(namespace)

    # AND the error message should be user-friendly
    error_message = str(exc_info.value)
    assert "Workflow module not found:" in error_message
    assert "some_external_package" in error_message

    assert exc_info.value.raw_data is not None
    assert exc_info.value.raw_data["vellum_on_error_action"] == "CREATE_CUSTOM_IMAGE"


def test_load_from_module__module_not_found_error_with_internal_package():
    """
    Tests that when ModuleNotFoundError occurs for an internal module (containing the namespace),
    the exception does NOT include vellum_on_error_action in raw_data.
    """

    # GIVEN a workflow module that imports a non-existent internal module
    files = {
        "__init__.py": "",
        "workflow.py": """\
from vellum.workflows import BaseWorkflow
from .non_existent_module import SomeClass

class Workflow(BaseWorkflow):
    graph = None
""",
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    finder = VirtualFileFinder(files, namespace, source_module="test")
    sys.meta_path.append(finder)

    # WHEN we attempt to load the workflow
    # THEN it should raise WorkflowInitializationException
    with pytest.raises(WorkflowInitializationException) as exc_info:
        BaseWorkflow.load_from_module(namespace)

    # AND the error message should be user-friendly
    error_message = str(exc_info.value)
    assert "Workflow module not found:" in error_message

    assert exc_info.value.raw_data is None


def test_serialize_module__tool_calling_node_with_single_tool():
    """Test that serialize_module works with a tool calling node that has a single tool."""

    # GIVEN a simple tool function
    tool_function_code = '''def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    return f"The weather in {location} is sunny."
'''

    # AND a workflow module with a tool calling node using that single tool
    files = {
        "__init__.py": "",
        "workflow.py": """
from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.displayable.tool_calling_node import ToolCallingNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseInputs
from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.variable_prompt_block import VariablePromptBlock

from .get_weather import get_weather


class Inputs(BaseInputs):
    location: str


class WeatherNode(ToolCallingNode):
    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        VariablePromptBlock(
                            input_variable="location",
                        ),
                    ],
                ),
            ],
        ),
    ]
    functions = [get_weather]
    prompt_inputs = {
        "location": Inputs.location,
    }


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = WeatherNode

    class Outputs(BaseWorkflow.Outputs):
        result = WeatherNode.Outputs.text
""",
        "get_weather.py": tool_function_code,
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    sys.meta_path.append(VirtualFileFinder(files, namespace))

    result = BaseWorkflowDisplay.serialize_module(namespace)

    # THEN the serialization should complete successfully
    assert result is not None


def test_resolve_workflow_deployment__returns_workflow_with_generated_files():
    """
    Test that resolve_workflow_deployment returns a workflow with artifacts
    in generated_files using the correct prefix format.
    """
    # GIVEN a deployment name and release tag
    deployment_name = "test_deployment"
    release_tag = "LATEST"

    expected_prefix = generate_workflow_deployment_prefix(deployment_name, release_tag)

    # Create a simple test node for the resolved workflow
    test_node_code = """
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.outputs import BaseOutputs

class TestNode(BaseNode):
    template = "Hello"

    class Outputs(BaseOutputs):
        result: str

    def run(self):
        return self.Outputs(result="Hello, {template}")
"""

    mock_workflow_code = """
from vellum.workflows import BaseWorkflow
from .nodes.test_node import TestNode

class ResolvedWorkflow(BaseWorkflow):
    graph = TestNode
"""

    # Create parent workflow files that reference the subworkflow deployment
    parent_workflow_code = """
from vellum.workflows import BaseWorkflow
from .nodes.subworkflow_deployment_node import TestSubworkflowDeploymentNode

class ParentWorkflow(BaseWorkflow):
    graph = TestSubworkflowDeploymentNode
"""

    parent_node_code = """
from vellum.workflows.nodes import SubworkflowDeploymentNode
from vellum.workflows.outputs import BaseOutputs

class TestSubworkflowDeploymentNode(SubworkflowDeploymentNode):
    deployment = "test_deployment"

    class Outputs(BaseOutputs):
        result: str

    subworkflow_inputs = {"message": "test"}
"""

    files = {
        "__init__.py": "",
        "workflow.py": parent_workflow_code,
        "nodes/__init__.py": """
from .subworkflow_deployment_node import TestSubworkflowDeploymentNode

__all__ = ["TestSubworkflowDeploymentNode"]
""",
        "nodes/subworkflow_deployment_node.py": parent_node_code,
        f"{expected_prefix}/__init__.py": "",
        f"{expected_prefix}/workflow.py": mock_workflow_code,
        f"{expected_prefix}/nodes/__init__.py": """
from .test_node import TestNode

__all__ = ["TestNode"]
""",
        f"{expected_prefix}/nodes/test_node.py": test_node_code,
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    finder = VirtualFileFinder(files, namespace)
    sys.meta_path.append(finder)

    # WHEN we execute the root workflow
    Workflow = BaseWorkflow.load_from_module(namespace)
    workflow = Workflow(context=WorkflowContext(generated_files=files, namespace=namespace))

    # THEN the workflow should be successfully initialized
    assert workflow

    event = workflow.run()

    # AND the method should return a workflow (not None) - this will pass once implemented
    assert event.name == "workflow.execution.fulfilled"


def test_resolve_workflow_deployment__uses_pull_api_with_inputs_deployment_name(vellum_client):
    """
    Test that resolve_workflow_deployment uses the pull API to fetch subworkflow files
    when the deployment name comes from Inputs.deployment_name.
    """
    # GIVEN a deployment name and release tag
    deployment_name = "test_deployment"
    release_tag = "LATEST"

    test_node_code = """
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.outputs import BaseOutputs

class TestNode(BaseNode):
    template = "Hello"

    class Outputs(BaseOutputs):
        result: str

    def run(self):
        return self.Outputs(result="Hello, {template}")
"""

    mock_workflow_code = """
from vellum.workflows import BaseWorkflow
from .nodes.test_node import TestNode

class ResolvedWorkflow(BaseWorkflow):
    graph = TestNode
"""

    inputs_code = """
from vellum.workflows.inputs import BaseInputs

class Inputs(BaseInputs):
    deployment_name: str
"""

    parent_workflow_code = """
from vellum.workflows import BaseWorkflow
from .inputs import Inputs
from .nodes.subworkflow_deployment_node import TestSubworkflowDeploymentNode
from vellum.workflows.state import BaseState

class ParentWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = TestSubworkflowDeploymentNode
"""

    parent_node_code = """
from vellum.workflows.nodes import SubworkflowDeploymentNode
from vellum.workflows.outputs import BaseOutputs
from ..inputs import Inputs

class TestSubworkflowDeploymentNode(SubworkflowDeploymentNode):
    deployment = Inputs.deployment_name

    class Outputs(BaseOutputs):
        result: str

    subworkflow_inputs = {"message": "test"}
"""

    subworkflow_files = {
        "__init__.py": "",
        "workflow.py": mock_workflow_code,
        "nodes/__init__.py": """
from .test_node import TestNode

__all__ = ["TestNode"]
""",
        "nodes/test_node.py": test_node_code,
    }

    parent_files = {
        "__init__.py": "",
        "inputs.py": inputs_code,
        "workflow.py": parent_workflow_code,
        "nodes/__init__.py": """
from .subworkflow_deployment_node import TestSubworkflowDeploymentNode

__all__ = ["TestSubworkflowDeploymentNode"]
""",
        "nodes/subworkflow_deployment_node.py": parent_node_code,
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered for the parent workflow
    finder = VirtualFileFinder(parent_files, namespace)
    sys.meta_path.append(finder)

    vellum_client.workflows.pull.return_value = iter([zip_file_map(subworkflow_files)])

    # WHEN we execute the root workflow with the mocked client
    Workflow = BaseWorkflow.load_from_module(namespace)
    Inputs = Workflow.get_inputs_class()

    workflow = Workflow(context=WorkflowContext(namespace=namespace, generated_files=parent_files))
    final_event = workflow.run(inputs=Inputs(deployment_name=deployment_name))

    # THEN the method should return a workflow (not None) - this will pass once implemented
    assert final_event.name == "workflow.execution.fulfilled", final_event

    # AND the pull API should have been called with the correct deployment name, release tag, and version
    args, kwargs = vellum_client.workflows.pull.call_args
    assert args[0] == deployment_name
    assert kwargs["release_tag"] == release_tag
    assert kwargs["version"].startswith(">=")
    assert ".0.0,<=" in kwargs["version"]

    # AND the X-Vellum-Always-Success header should be included for graceful error handling
    assert kwargs["request_options"]["additional_headers"]["X-Vellum-Always-Success"] == "true"
