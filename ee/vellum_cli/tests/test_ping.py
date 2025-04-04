from datetime import datetime

from click.testing import CliRunner

from vellum.client.core.api_error import ApiError
from vellum.client.types.organization_read import OrganizationRead
from vellum.client.types.workspace_read import WorkspaceRead
from vellum_cli import main as cli_main


def test_ping__happy_path(vellum_client):
    # GIVEN a cli
    runner = CliRunner()

    # AND a valid response from both the workflow and organization API calls
    vellum_client.workspaces.workspace_identity.return_value = WorkspaceRead(
        id="1234567890",
        name="Test Workspace",
        label="Test Workspace",
        created=datetime.now(),
    )
    vellum_client.organizations.organization_identity.return_value = OrganizationRead(
        id="1234567890",
        name="Test Organization",
        new_member_join_behavior="AUTO_ACCEPT_FROM_SHARED_DOMAIN",
        allow_staff_access=True,
    )

    # WHEN calling `vellum ping`
    result = runner.invoke(cli_main, ["ping"])

    # THEN it should return Status information about the user's workspace
    assert result.exit_code == 0
    assert (
        result.output
        == """\x1b[38;20m\
Successfully authenticated with Vellum!

Organization:
    ID: 1234567890
    Name: Test Organization

Workspace:
    ID: 1234567890
    Name: Test Workspace
\x1b[0m
"""
    )


def test_ping__error_path(vellum_client):
    # GIVEN a cli
    runner = CliRunner()

    vellum_client.workspaces.workspace_identity.side_effect = ApiError(status_code=400, body="Invalid JSON")

    # WHEN the user runs the ping command
    result = runner.invoke(cli_main, ["ping"])

    # THEN the command returns an error
    assert result.exit_code == 1
    assert (
        str(result.exception)
        == "The API we tried to ping returned an invalid response. Please make sure your `VELLUM_API_URL` environment variable is set correctly."  # noqa: E501
    )


def test_ping__unauthorized_error_path(vellum_client):
    # GIVEN a cli
    runner = CliRunner()

    # GIVEN an unauthorized error with the error message from the API
    vellum_client.workspaces.workspace_identity.side_effect = ApiError(
        status_code=403, body={"detail": "Authentication credentials were not provided."}
    )

    # WHEN the user runs the ping command
    result = runner.invoke(cli_main, ["ping"])

    # THEN the command returns an error
    assert result.exit_code == 1
    assert str(result.exception) == "Please make sure your `VELLUM_API_KEY` environment variable is set correctly."
