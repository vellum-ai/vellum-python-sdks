import pytest

from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.displayable.code_execution_node.utils import run_code_inline


def test_run_code_inline__error_handling(vellum_client):
    """
    Tests that run_code_inline properly handles exceptions in user code
    and formats the traceback correctly.
    """
    # GIVEN code that will raise an exception
    code = """
import json

def main(data):
    # This will raise a TypeError because 'undefined' is not JSON serializable
    return json.dumps(data)
"""

    # AND a mock undefined class that is not JSON serializable
    class undefined:
        pass

    inputs = {"data": undefined()}

    # WHEN we run the code inline
    # THEN it should raise a NodeException with a formatted traceback
    with pytest.raises(NodeException) as exc_info:
        run_code_inline(
            code=code,
            inputs=inputs,
            output_type=str,
            filepath="test_script.py",
            vellum_client=vellum_client,
        )

    # AND the error message should contain the traceback information
    assert "TypeError" in exc_info.value.message
    assert "not JSON serializable" in exc_info.value.message
