import pytest
from uuid import UUID

from vellum.workflows.types.definition import DeploymentDefinition


@pytest.mark.parametrize(
    "deployment_value, expected_deployment_id, expected_deployment_name",
    [
        # Valid UUID string
        (
            "57f09beb-b463-40e0-bf9e-c972e664352f",
            UUID("57f09beb-b463-40e0-bf9e-c972e664352f"),
            None,
        ),
        # Name string
        (
            "tool-calling-subworkflow",
            None,
            "tool-calling-subworkflow",
        ),
    ],
    ids=[
        "valid_uuid",
        "valid_name",
    ],
)
def test_deployment_definition(deployment_value, expected_deployment_id, expected_deployment_name):
    """Test that DeploymentDefinition properties correctly identify and extract UUID vs name."""
    deployment = DeploymentDefinition(deployment=deployment_value)

    assert deployment.deployment_id == expected_deployment_id
    assert deployment.deployment_name == expected_deployment_name
