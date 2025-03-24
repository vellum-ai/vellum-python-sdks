import pytest

from vellum.workflows.nodes import BaseNode
from vellum.workflows.references.lazy import LazyReference


@pytest.fixture
def mock_inspect_getsource(mocker):
    return mocker.patch("inspect.getsource")


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("vellum.workflows.references.lazy.logger")


def test_lazy_reference__inspect_getsource_fails(mock_inspect_getsource, mock_logger):
    # GIVEN getsource fails to resolve the lambda's source code
    mock_inspect_getsource.side_effect = Exception("test")

    # WHEN a node with a lazy reference is defined
    class MyNode(BaseNode):
        lazy_reference = LazyReference(lambda: MyNode.Outputs.foo)

    # THEN the name is the lambda function's name
    assert MyNode.lazy_reference.instance
    assert MyNode.lazy_reference.instance.name == "<lambda>"

    # AND sentry is notified
    assert mock_logger.exception.call_count == 1
