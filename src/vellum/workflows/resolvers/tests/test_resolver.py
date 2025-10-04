from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4
from typing import List

from vellum import ChatMessage
from vellum.client.types.workflow_resolved_state import WorkflowResolvedState
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.resolvers.resolver import VellumResolver
from vellum.workflows.resolvers.types import LoadStateResult
from vellum.workflows.state.base import BaseState, NodeExecutionCache
from vellum.workflows.state.context import WorkflowContext


def test_load_state_with_context_success():
    """Test load_state successfully loads state when context and client are available."""
    resolver = VellumResolver()
    execution_id = uuid4()

    class TestState(BaseState):
        test_key: str = "test_value"

    class TestWorkflow(BaseWorkflow[BaseInputs, TestState]):
        pass

    # GIVEN a state dictionary that matches what the resolver expects
    prev_id = str(uuid4())
    prev_span_id = str(uuid4())
    state_dict = {
        "test_key": "test_value",
        "meta": {
            "workflow_definition": "MockWorkflow",
            "id": prev_id,
            "span_id": prev_span_id,
            "updated_ts": datetime.now().isoformat(),
            "workflow_inputs": BaseInputs(),
            "external_inputs": {},
            "node_outputs": {},
            "node_execution_cache": NodeExecutionCache(),
            "parent": None,
        },
    }

    previous_trace_id = str(uuid4())
    previous_span_id = str(uuid4())
    root_trace_id = str(uuid4())
    root_span_id = str(uuid4())

    mock_response = WorkflowResolvedState(
        trace_id=str(uuid4()),
        timestamp=datetime.now(),
        span_id=str(execution_id),
        state=state_dict,
        previous_trace_id=previous_trace_id,
        previous_span_id=previous_span_id,
        root_trace_id=root_trace_id,
        root_span_id=root_span_id,
    )

    mock_client = Mock()
    mock_client.workflows.retrieve_state.return_value = mock_response

    # AND context with the test workflow class is set up
    context = WorkflowContext(vellum_client=mock_client)
    TestWorkflow(context=context, resolvers=[resolver])

    # WHEN load_state is called
    result = resolver.load_state(previous_execution_id=execution_id)

    # THEN should return LoadStateResult with state and span link info
    assert isinstance(result, LoadStateResult)
    assert result.state is not None
    assert isinstance(result.state, TestState)
    assert result.state.test_key == "test_value"

    # AND the new state should have different meta IDs than those provided in the loaded state_dict
    assert str(result.state.meta.id) != prev_id
    assert str(result.state.meta.span_id) != prev_span_id

    # AND should have span link info
    assert result.previous_trace_id == previous_trace_id
    assert result.previous_span_id == previous_span_id
    assert result.root_trace_id == root_trace_id
    assert result.root_span_id == root_span_id

    mock_client.workflows.retrieve_state.assert_called_once_with(span_id=str(execution_id))


def test_load_state_with_chat_message_list():
    """Test load_state successfully loads state with chat_history containing ChatMessage list."""
    resolver = VellumResolver()
    execution_id = uuid4()

    class TestStateWithChatHistory(BaseState):
        test_key: str = "test_value"
        chat_history: List[ChatMessage] = []

    class TestWorkflow(BaseWorkflow[BaseInputs, TestStateWithChatHistory]):
        pass

    # GIVEN a state dictionary with chat_history containing ChatMessage objects
    prev_id = str(uuid4())
    prev_span_id = str(uuid4())
    state_dict = {
        "test_key": "test_value",
        "chat_history": [
            {"role": "USER", "text": "Hello, how are you?"},
            {"role": "ASSISTANT", "text": "I'm doing well, thank you!"},
            {"role": "USER", "text": "What can you help me with?"},
        ],
        "meta": {
            "workflow_definition": "MockWorkflow",
            "id": prev_id,
            "span_id": prev_span_id,
            "updated_ts": datetime.now().isoformat(),
            "workflow_inputs": BaseInputs(),
            "external_inputs": {},
            "node_outputs": {},
            "node_execution_cache": NodeExecutionCache(),
            "parent": None,
        },
    }

    previous_trace_id = str(uuid4())
    previous_span_id = str(uuid4())
    root_trace_id = str(uuid4())
    root_span_id = str(uuid4())

    mock_response = WorkflowResolvedState(
        trace_id=str(uuid4()),
        timestamp=datetime.now(),
        span_id=str(execution_id),
        state=state_dict,
        previous_trace_id=previous_trace_id,
        previous_span_id=previous_span_id,
        root_trace_id=root_trace_id,
        root_span_id=root_span_id,
    )

    mock_client = Mock()
    mock_client.workflows.retrieve_state.return_value = mock_response

    # AND context with the test workflow class is set up
    context = WorkflowContext(vellum_client=mock_client)
    TestWorkflow(context=context, resolvers=[resolver])

    # WHEN load_state is called
    result = resolver.load_state(previous_execution_id=execution_id)

    # THEN should return LoadStateResult with state containing chat_history
    assert isinstance(result, LoadStateResult)
    assert result.state is not None
    assert isinstance(result.state, TestStateWithChatHistory)
    assert result.state.test_key == "test_value"

    # AND the chat_history should be properly deserialized as ChatMessage objects
    assert len(result.state.chat_history) == 3
    assert all(isinstance(msg, ChatMessage) for msg in result.state.chat_history)
    assert result.state.chat_history[0].role == "USER"
    assert result.state.chat_history[0].text == "Hello, how are you?"
    assert result.state.chat_history[1].role == "ASSISTANT"
    assert result.state.chat_history[1].text == "I'm doing well, thank you!"
    assert result.state.chat_history[2].role == "USER"
    assert result.state.chat_history[2].text == "What can you help me with?"

    mock_client.workflows.retrieve_state.assert_called_once_with(span_id=str(execution_id))
