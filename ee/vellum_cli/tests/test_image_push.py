import pytest
import json
import os
import shutil
import subprocess
import tempfile
from unittest.mock import MagicMock, patch
from uuid import uuid4
from typing import Generator

from click.testing import CliRunner
from httpx import Response

from vellum_cli import main as cli_main


@pytest.fixture
def mock_temp_dir() -> Generator[str, None, None]:
    current_dir = os.getcwd()
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)

    yield temp_dir

    os.chdir(current_dir)
    shutil.rmtree(temp_dir)


@patch("subprocess.run")
@patch("docker.from_env")
def test_image_push__self_hosted_happy_path(mock_docker_from_env, mock_run, vellum_client, monkeypatch):
    # GIVEN a self hosted vellum api URL env var
    monkeypatch.setenv("VELLUM_API_URL", "mycompany.api.com")
    monkeypatch.setenv("VELLUM_API_KEY", "123456abcdef")

    # Mock Docker client
    mock_docker_client = MagicMock()
    mock_docker_from_env.return_value = mock_docker_client

    mock_run.side_effect = [
        subprocess.CompletedProcess(
            args="", returncode=0, stdout=b'{"manifests": [{"platform": {"architecture": "amd64"}}]}'
        ),
        subprocess.CompletedProcess(args="", returncode=0, stdout=b"manifest"),
        subprocess.CompletedProcess(args="", returncode=0, stdout=b"sha256:hellosha"),
    ]

    # WHEN the user runs the image push command
    runner = CliRunner()
    result = runner.invoke(cli_main, ["image", "push", "myrepo.net/myimage:latest"])

    # THEN the command exits successfully
    assert result.exit_code == 0, result.output

    # AND gives the success message
    assert "Image successfully pushed" in result.output


@patch("subprocess.run")
@patch("docker.from_env")
def test_image_push__self_hosted_happy_path__workspace_option(
    mock_docker_from_env, mock_run, mock_httpx_transport, mock_temp_dir
):
    # GIVEN a workspace config with a new env for url
    with open(os.path.join(mock_temp_dir, "vellum.lock.json"), "w") as f:
        f.write(
            json.dumps(
                {
                    "workspaces": [
                        {
                            "name": "my_workspace",
                            "api_url": "MY_WORKSPACE_VELLUM_API_URL",
                            "api_key": "MY_WORKSPACE_VELLUM_API_KEY",
                        }
                    ]
                }
            )
        )

    # AND a .env file with the workspace api key and url
    with open(os.path.join(mock_temp_dir, ".env"), "w") as f:
        f.write(
            "VELLUM_API_KEY=123456abcdef\n"
            "VELLUM_API_URL=https://api.vellum.ai\n"
            "MY_WORKSPACE_VELLUM_API_KEY=789012ghijkl\n"
            "MY_WORKSPACE_VELLUM_API_URL=https://api.vellum.mycompany.ai\n"
        )

    # AND the Docker client returns the correct response
    mock_docker_client = MagicMock()
    mock_docker_from_env.return_value = mock_docker_client

    mock_run.side_effect = [
        subprocess.CompletedProcess(
            args="", returncode=0, stdout=b'{"manifests": [{"platform": {"architecture": "amd64"}}]}'
        ),
        subprocess.CompletedProcess(args="", returncode=0, stdout=b"sha256:hellosha"),
    ]

    # AND the vellum client returns the correct response for
    mock_httpx_transport.handle_request.side_effect = [
        # First call to get the docker service token
        Response(
            status_code=200,
            text=json.dumps(
                {
                    "access_token": "345678mnopqr",
                    "organization_id": str(uuid4()),
                    "repository": "myrepo.net",
                }
            ),
        ),
        # Second call to push the image
        Response(
            status_code=200,
            text=json.dumps(
                {
                    "id": str(uuid4()),
                    "name": "myrepo.net/myimage",
                    "visibility": "PRIVATE",
                    "created": "2021-01-01T00:00:00Z",
                    "modified": "2021-01-01T00:00:00Z",
                    "repository": "myrepo.net",
                    "sha": "sha256:hellosha",
                    "tags": [],
                }
            ),
        ),
    ]

    # WHEN the user runs the image push command
    runner = CliRunner()
    result = runner.invoke(cli_main, ["image", "push", "myrepo.net/myimage:latest", "--workspace", "my_workspace"])

    # THEN the command exits successfully
    assert result.exit_code == 0, (result.output, str(result.exception))

    # AND gives the success message
    assert "Image successfully pushed" in result.output

    # AND the vellum client was called with the correct api key and url
    request = mock_httpx_transport.handle_request.call_args[0][0]
    assert request.headers["X-API-KEY"] == "789012ghijkl", result.stdout
    assert str(request.url) == "https://api.vellum.mycompany.ai/v1/container-images/push"


@patch("subprocess.run")
@patch("docker.from_env")
def test_image_push__self_hosted_blocks_repo(mock_docker_from_env, mock_run, vellum_client, monkeypatch):
    # GIVEN a self hosted vellum api URL env var
    monkeypatch.setenv("VELLUM_API_URL", "mycompany.api.com")

    # Mock Docker client
    mock_docker_client = MagicMock()
    mock_docker_from_env.return_value = mock_docker_client

    # WHEN the user runs the image push command
    runner = CliRunner()
    result = runner.invoke(cli_main, ["image", "push", "myimage"])

    # THEN the command exits unsuccessfully
    assert result.exit_code == 1, result.output

    # AND gives the error message for self hosted installs not including the repo
    assert "For adding images to your self hosted install you must include" in result.output
