import pytest
import json
import os
import shutil
import subprocess
import tempfile
from unittest.mock import MagicMock
from uuid import uuid4
from typing import Generator

from click.testing import CliRunner
from httpx import Response

from vellum.client.types.docker_service_token import DockerServiceToken
from vellum_cli import main as cli_main


@pytest.fixture
def mock_temp_dir() -> Generator[str, None, None]:
    current_dir = os.getcwd()
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)

    yield temp_dir

    os.chdir(current_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_docker_from_env(mocker):
    return mocker.patch("docker.from_env")


@pytest.fixture
def mock_subprocess_run(mocker):
    return mocker.patch("subprocess.run")


@pytest.mark.usefixtures("vellum_client", "info_log_level")
def test_image_push__self_hosted_happy_path(mock_docker_from_env, mock_subprocess_run, monkeypatch):
    # GIVEN a self hosted vellum api URL env var
    monkeypatch.setenv("VELLUM_API_URL", "mycompany.api.com")
    monkeypatch.setenv("VELLUM_API_KEY", "123456abcdef")

    # Mock Docker client
    mock_docker_client = MagicMock()
    mock_docker_from_env.return_value = mock_docker_client

    mock_subprocess_run.side_effect = [
        subprocess.CompletedProcess(args="", returncode=0, stdout=b"Pruning successful"),
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


@pytest.mark.usefixtures("info_log_level")
def test_image_push__self_hosted_happy_path__workspace_option(
    mock_docker_from_env, mock_subprocess_run, mock_httpx_transport, mock_temp_dir
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

    mock_subprocess_run.side_effect = [
        subprocess.CompletedProcess(args="", returncode=0, stdout=b"Pruning successful"),
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


@pytest.mark.usefixtures("vellum_client", "mock_subprocess_run")
def test_image_push__self_hosted_blocks_repo(mock_docker_from_env, monkeypatch):
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


@pytest.mark.usefixtures("info_log_level")
def test_image_push_with_source_success(
    mock_docker_from_env, mock_subprocess_run, vellum_client, monkeypatch, mock_temp_dir
):
    monkeypatch.setenv("VELLUM_API_URL", "https://api.vellum.ai")
    monkeypatch.setenv("VELLUM_API_KEY", "123456abcdef")

    dockerfile_path = os.path.join(mock_temp_dir, "Dockerfile")
    with open(dockerfile_path, "w") as f:
        f.write("FROM alpine:latest\n")

    mock_docker_client = MagicMock()
    mock_docker_from_env.return_value = mock_docker_client
    mock_docker_client.images.push.return_value = [b'{"status": "Pushed"}']

    mock_subprocess_run.side_effect = [
        subprocess.CompletedProcess(args="", returncode=0, stdout=b"Pruning successful"),
        subprocess.CompletedProcess(args="", returncode=0, stdout=b"Build successful"),
        subprocess.CompletedProcess(
            args="", returncode=0, stdout=b'{"manifests": [{"platform": {"architecture": "amd64"}}]}'
        ),
        subprocess.CompletedProcess(args="", returncode=0, stdout=b"sha256:hellosha"),
    ]

    vellum_client.container_images.docker_service_token.return_value = DockerServiceToken(
        access_token="345678mnopqr", organization_id="test-org", repository="myrepo.net"
    )

    runner = CliRunner()
    result = runner.invoke(cli_main, ["image", "push", "myimage:latest", "--source", dockerfile_path])

    assert result.exit_code == 0, result.output

    build_call = mock_subprocess_run.call_args_list[1]
    assert build_call[0][0] == [
        "docker",
        "buildx",
        "build",
        "-f",
        dockerfile_path,
        "--platform=linux/amd64",
        "-t",
        "myimage:latest",
        ".",
    ]

    assert "Docker build completed successfully" in result.output
    assert "Image successfully pushed" in result.output


@pytest.mark.usefixtures("mock_docker_from_env", "mock_subprocess_run", "vellum_client")
def test_image_push_with_source_dockerfile_not_exists(monkeypatch, mock_temp_dir):
    monkeypatch.setenv("VELLUM_API_URL", "https://api.vellum.ai")
    monkeypatch.setenv("VELLUM_API_KEY", "123456abcdef")

    nonexistent_dockerfile = os.path.join(mock_temp_dir, "nonexistent_dockerfile")

    runner = CliRunner()
    result = runner.invoke(cli_main, ["image", "push", "myimage:latest", "--source", nonexistent_dockerfile])

    assert result.exit_code == 1
    assert "Dockerfile does not exist" in result.output


@pytest.mark.usefixtures("mock_docker_from_env", "vellum_client")
def test_image_push_with_source_build_fails(mock_subprocess_run, monkeypatch, mock_temp_dir):
    monkeypatch.setenv("VELLUM_API_URL", "https://api.vellum.ai")
    monkeypatch.setenv("VELLUM_API_KEY", "123456abcdef")

    dockerfile_path = os.path.join(mock_temp_dir, "Dockerfile")
    with open(dockerfile_path, "w") as f:
        f.write("FROM alpine:latest\n")

    mock_subprocess_run.side_effect = [
        subprocess.CompletedProcess(args="", returncode=0, stdout=b"Pruning successful"),
        subprocess.CompletedProcess(args="", returncode=1, stderr=b"Build failed: missing dependency"),
    ]

    runner = CliRunner()
    result = runner.invoke(cli_main, ["image", "push", "myimage:latest", "--source", dockerfile_path])

    assert result.exit_code == 1
    assert "Docker build failed" in result.output
    assert "Build failed: missing dependency" in result.output


@pytest.mark.usefixtures("vellum_client", "info_log_level")
def test_image_push_includes_docker_prune(mock_docker_from_env, mock_subprocess_run, monkeypatch):
    """
    Tests that image_push_command calls docker image prune before validation.
    """
    # GIVEN a self hosted vellum api URL env var
    monkeypatch.setenv("VELLUM_API_URL", "mycompany.api.com")
    monkeypatch.setenv("VELLUM_API_KEY", "123456abcdef")

    # AND a mock Docker client
    mock_docker_client = MagicMock()
    mock_docker_from_env.return_value = mock_docker_client

    mock_subprocess_run.side_effect = [
        subprocess.CompletedProcess(args="", returncode=0, stdout=b"Pruning successful"),
        subprocess.CompletedProcess(
            args="", returncode=0, stdout=b'{"manifests": [{"platform": {"architecture": "amd64"}}]}'
        ),
        subprocess.CompletedProcess(args="", returncode=0, stdout=b"manifest"),
        subprocess.CompletedProcess(args="", returncode=0, stdout=b"sha256:hellosha"),
    ]

    # WHEN the user runs the image push command with any image
    runner = CliRunner()
    result = runner.invoke(cli_main, ["image", "push", "myrepo.net/myimage:latest"])

    # THEN the command exits successfully
    assert result.exit_code == 0, result.output

    prune_call = mock_subprocess_run.call_args_list[0]
    assert prune_call[0][0] == [
        "docker",
        "image",
        "prune",
        "--all",
        "-f",
        "--filter",
        "label=image-type=python-workflow-runtime",
    ]

    # AND the success message includes pruning completion
    assert "Docker image pruning completed successfully" in result.output


@pytest.mark.usefixtures("vellum_client", "info_log_level")
def test_image_push_continues_if_prune_fails(mock_docker_from_env, mock_subprocess_run, monkeypatch):
    """
    Tests that image_push_command continues if docker image prune fails.
    """
    # GIVEN a self hosted vellum api URL env var
    monkeypatch.setenv("VELLUM_API_URL", "mycompany.api.com")
    monkeypatch.setenv("VELLUM_API_KEY", "123456abcdef")

    # AND a mock Docker client
    mock_docker_client = MagicMock()
    mock_docker_from_env.return_value = mock_docker_client

    mock_subprocess_run.side_effect = [
        subprocess.CalledProcessError(
            1, ["docker", "image", "prune", "--all", "-f", "--filter", "label=image-type=python-workflow-runtime"]
        ),
        subprocess.CompletedProcess(
            args="", returncode=0, stdout=b'{"manifests": [{"platform": {"architecture": "amd64"}}]}'
        ),
        subprocess.CompletedProcess(args="", returncode=0, stdout=b"manifest"),
        subprocess.CompletedProcess(args="", returncode=0, stdout=b"sha256:hellosha"),
    ]

    # WHEN the user runs the image push command with any image
    runner = CliRunner()
    result = runner.invoke(cli_main, ["image", "push", "myrepo.net/myimage:latest"])

    # THEN the command exits successfully despite pruning failure
    assert result.exit_code == 0, result.output

    # AND the warning message about pruning failure is shown
    assert "Docker image pruning failed" in result.output

    # AND the success message is still shown
    assert "Image successfully pushed" in result.output
