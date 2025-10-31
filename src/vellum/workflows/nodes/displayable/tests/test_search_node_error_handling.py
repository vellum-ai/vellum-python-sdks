import pytest

from vellum.client.core.api_error import ApiError
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.displayable.search_node import SearchNode as BaseSearchNode
from vellum.workflows.state import BaseState
from vellum.workflows.state.base import StateMeta


def test_search_node_handles_403_error(vellum_client):
    """Test that SearchNode properly handles 403 API errors with user-facing messages."""

    class Inputs(BaseInputs):
        query: str
        document_index: str

    class State(BaseState):
        pass

    class SearchNode(BaseSearchNode):
        query = Inputs.query
        document_index = Inputs.document_index

    vellum_client.search.side_effect = ApiError(
        status_code=403, body={"detail": "Provider credentials is missing or unavailable"}
    )

    node = SearchNode(
        state=State(
            meta=StateMeta(
                workflow_inputs=Inputs(
                    query="test query",
                    document_index="test-index",
                )
            ),
        )
    )

    with pytest.raises(NodeException) as exc_info:
        node.run()

    assert exc_info.value.code == WorkflowErrorCode.PROVIDER_CREDENTIALS_UNAVAILABLE
    assert exc_info.value.message == "Provider credentials is missing or unavailable"


def test_search_node_handles_403_error_with_custom_detail(vellum_client):
    """Test that SearchNode properly handles 403 API errors with custom detail message."""

    class Inputs(BaseInputs):
        query: str
        document_index: str

    class State(BaseState):
        pass

    class SearchNode(BaseSearchNode):
        query = Inputs.query
        document_index = Inputs.document_index

    vellum_client.search.side_effect = ApiError(status_code=403, body={"detail": "Access denied to document index"})

    node = SearchNode(
        state=State(
            meta=StateMeta(
                workflow_inputs=Inputs(
                    query="test query",
                    document_index="test-index",
                )
            ),
        )
    )

    with pytest.raises(NodeException) as exc_info:
        node.run()

    assert exc_info.value.code == WorkflowErrorCode.PROVIDER_CREDENTIALS_UNAVAILABLE
    assert exc_info.value.message == "Access denied to document index"


def test_search_node_handles_403_error_without_detail(vellum_client):
    """Test that SearchNode properly handles 403 API errors without detail in body."""

    class Inputs(BaseInputs):
        query: str
        document_index: str

    class State(BaseState):
        pass

    class SearchNode(BaseSearchNode):
        query = Inputs.query
        document_index = Inputs.document_index

    vellum_client.search.side_effect = ApiError(status_code=403, body={})

    node = SearchNode(
        state=State(
            meta=StateMeta(
                workflow_inputs=Inputs(
                    query="test query",
                    document_index="test-index",
                )
            ),
        )
    )

    with pytest.raises(NodeException) as exc_info:
        node.run()

    assert exc_info.value.code == WorkflowErrorCode.PROVIDER_CREDENTIALS_UNAVAILABLE
    assert exc_info.value.message == "Provider credentials is missing or unavailable"


def test_search_node_handles_other_4xx_errors(vellum_client):
    """Test that SearchNode properly handles other 4xx API errors."""

    class Inputs(BaseInputs):
        query: str
        document_index: str

    class State(BaseState):
        pass

    class SearchNode(BaseSearchNode):
        query = Inputs.query
        document_index = Inputs.document_index

    vellum_client.search.side_effect = ApiError(status_code=400, body={"detail": "Invalid request parameters"})

    node = SearchNode(
        state=State(
            meta=StateMeta(
                workflow_inputs=Inputs(
                    query="test query",
                    document_index="test-index",
                )
            ),
        )
    )

    with pytest.raises(NodeException) as exc_info:
        node.run()

    assert exc_info.value.code == WorkflowErrorCode.INVALID_INPUTS
    assert "Invalid request parameters" in exc_info.value.message


def test_search_node_handles_5xx_errors(vellum_client):
    """Test that SearchNode properly handles 5xx API errors as internal errors."""

    class Inputs(BaseInputs):
        query: str
        document_index: str

    class State(BaseState):
        pass

    class SearchNode(BaseSearchNode):
        query = Inputs.query
        document_index = Inputs.document_index

    vellum_client.search.side_effect = ApiError(status_code=500, body={"detail": "Internal server error"})

    node = SearchNode(
        state=State(
            meta=StateMeta(
                workflow_inputs=Inputs(
                    query="test query",
                    document_index="test-index",
                )
            ),
        )
    )

    with pytest.raises(NodeException) as exc_info:
        node.run()

    assert exc_info.value.code == WorkflowErrorCode.INTERNAL_ERROR
    assert "An error occurred while searching against Document Index 'test-index'" in exc_info.value.message


def test_search_node_handles_api_error_without_status_code(vellum_client):
    """Test that SearchNode properly handles API errors without status code."""

    class Inputs(BaseInputs):
        query: str
        document_index: str

    class State(BaseState):
        pass

    class SearchNode(BaseSearchNode):
        query = Inputs.query
        document_index = Inputs.document_index

    vellum_client.search.side_effect = ApiError(status_code=None, body={"detail": "Unknown error"})

    node = SearchNode(
        state=State(
            meta=StateMeta(
                workflow_inputs=Inputs(
                    query="test query",
                    document_index="test-index",
                )
            ),
        )
    )

    with pytest.raises(NodeException) as exc_info:
        node.run()

    assert exc_info.value.code == WorkflowErrorCode.INTERNAL_ERROR
    assert "An error occurred while searching against Document Index 'test-index'" in exc_info.value.message


def test_search_node_includes_raw_data_in_403_error(vellum_client):
    """Test that SearchNode includes raw_data in 403 error responses."""

    # GIVEN a SearchNode configured with query and document_index
    class Inputs(BaseInputs):
        query: str
        document_index: str

    class State(BaseState):
        pass

    class SearchNode(BaseSearchNode):
        query = Inputs.query
        document_index = Inputs.document_index

    error_body = {
        "detail": "Provider credentials is missing or unavailable",
        "error_code": "CREDENTIALS_MISSING",
        "provider": "openai",
        "additional_info": "Please configure your API key",
    }
    vellum_client.search.side_effect = ApiError(status_code=403, body=error_body)

    node = SearchNode(
        state=State(
            meta=StateMeta(
                workflow_inputs=Inputs(
                    query="test query",
                    document_index="test-index",
                )
            ),
        )
    )

    with pytest.raises(NodeException) as exc_info:
        node.run()

    assert exc_info.value.raw_data == error_body


def test_search_node_includes_raw_data_in_4xx_error(vellum_client):
    """Test that SearchNode includes raw_data in 4xx error responses."""

    # GIVEN a SearchNode configured with query and document_index
    class Inputs(BaseInputs):
        query: str
        document_index: str

    class State(BaseState):
        pass

    class SearchNode(BaseSearchNode):
        query = Inputs.query
        document_index = Inputs.document_index

    error_body = {
        "detail": "Invalid request parameters",
        "error_code": "INVALID_PARAMS",
        "field_errors": {"query": "Query cannot be empty"},
    }
    vellum_client.search.side_effect = ApiError(status_code=400, body=error_body)

    node = SearchNode(
        state=State(
            meta=StateMeta(
                workflow_inputs=Inputs(
                    query="test query",
                    document_index="test-index",
                )
            ),
        )
    )

    with pytest.raises(NodeException) as exc_info:
        node.run()

    assert exc_info.value.raw_data == error_body


def test_search_node_includes_raw_data_in_5xx_error(vellum_client):
    """Test that SearchNode includes raw_data in 5xx error responses."""

    # GIVEN a SearchNode configured with query and document_index
    class Inputs(BaseInputs):
        query: str
        document_index: str

    class State(BaseState):
        pass

    class SearchNode(BaseSearchNode):
        query = Inputs.query
        document_index = Inputs.document_index

    error_body = {"detail": "Internal server error", "error_code": "INTERNAL_ERROR", "request_id": "req_123456"}
    vellum_client.search.side_effect = ApiError(status_code=500, body=error_body)

    node = SearchNode(
        state=State(
            meta=StateMeta(
                workflow_inputs=Inputs(
                    query="test query",
                    document_index="test-index",
                )
            ),
        )
    )

    with pytest.raises(NodeException) as exc_info:
        node.run()

    assert exc_info.value.raw_data == error_body
