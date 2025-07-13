from unittest.mock import Mock
from typing import List

from vellum import ChatMessage
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.string_chat_message_content import StringChatMessageContent
from vellum.workflows.nodes.displayable.tool_calling_node.utils import DynamicSubworkflowDeploymentNode
from vellum.workflows.state.base import BaseState, StateMeta
from vellum.workflows.state.context import WorkflowContext


def test_dynamic_subworkflow_deployment_node__with_function_call_output():
    """
    Test that DynamicSubworkflowDeploymentNode correctly processes function call output.
    """

    function_call_output: List[FunctionCallVellumValue] = [
        FunctionCallVellumValue(
            value=FunctionCall(
                arguments={"input1": "value1", "input2": "value2"},
                id="test-call-id",
                name="test-function",
                state="FULFILLED",
            )
        )
    ]

    mock_outputs = Mock()
    mock_outputs.results = Mock()
    mock_tool_router_class = Mock()
    mock_tool_router_class.Outputs = mock_outputs

    class TestDynamicNode(DynamicSubworkflowDeploymentNode):
        deployment = "test-deployment"
        tool_router_node_class = mock_tool_router_class

    mock_client = Mock()
    mock_output = Mock()
    mock_output.name = "result"
    mock_output.value = "test output"
    mock_client.execute_workflow_stream.return_value = iter(
        [
            Mock(type="WORKFLOW", data=Mock(state="INITIATED")),
            Mock(type="WORKFLOW", data=Mock(state="FULFILLED", outputs=[mock_output])),
        ]
    )

    class TestState(BaseState):
        chat_history: List[ChatMessage] = []

    context = WorkflowContext(vellum_client=mock_client)
    state = TestState()
    state.meta = StateMeta()
    state.meta.node_outputs = {mock_outputs.results: function_call_output}

    node = TestDynamicNode(context=context, state=state)
    list(node.run())

    assert len(state.chat_history) == 1
    assert state.chat_history[0].role == "FUNCTION"
    assert isinstance(state.chat_history[0].content, StringChatMessageContent)


def test_dynamic_subworkflow_deployment_node__empty_function_call_output():
    """
    Test that DynamicSubworkflowDeploymentNode handles empty function call output.
    """

    function_call_output: List[FunctionCallVellumValue] = []

    mock_outputs = Mock()
    mock_outputs.results = Mock()
    mock_tool_router_class = Mock()
    mock_tool_router_class.Outputs = mock_outputs

    class TestDynamicNode(DynamicSubworkflowDeploymentNode):
        deployment = "test-deployment"
        tool_router_node_class = mock_tool_router_class

    mock_client = Mock()
    mock_client.execute_workflow_stream.return_value = iter(
        [
            Mock(type="WORKFLOW", data=Mock(state="INITIATED")),
            Mock(type="WORKFLOW", data=Mock(state="FULFILLED", outputs=[])),
        ]
    )

    class TestState(BaseState):
        chat_history: List[ChatMessage] = []

    context = WorkflowContext(vellum_client=mock_client)
    state = TestState()
    state.meta = StateMeta()
    state.meta.node_outputs = {mock_outputs.results: function_call_output}

    node = TestDynamicNode(context=context, state=state)
    list(node.run())

    assert len(state.chat_history) == 1
    assert state.chat_history[0].role == "FUNCTION"
