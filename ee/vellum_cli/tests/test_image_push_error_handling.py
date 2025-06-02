import subprocess
from unittest.mock import patch
from uuid import uuid4

from click.testing import CliRunner

from vellum.client.core.api_error import ApiError
from vellum_cli import main as cli_main


@patch("subprocess.run")
@patch("docker.from_env")
def test_image_push_docker_service_token_401_error(mock_docker_from_env, mock_run, vellum_client, monkeypatch):
    monkeypatch.setenv("VELLUM_API_URL", "https://api.vellum.ai")
    monkeypatch.setenv("VELLUM_API_KEY", "123456abcdef")

    mock_docker_client = mock_docker_from_env.return_value
    mock_docker_client.images.get.return_value.id = "test-image-id"

    mock_run.side_effect = [
        subprocess.CompletedProcess(
            args="", returncode=0, stdout=b'{"manifests": [{"platform": {"architecture": "amd64"}}]}'
        ),
    ]

    vellum_client.container_images.docker_service_token.side_effect = ApiError(status_code=401, body="Unauthorized")

    runner = CliRunner()
    result = runner.invoke(cli_main, ["image", "push", "myimage:latest"])

    assert result.exit_code == 1
    assert "Authentication failed" in result.output
    assert "VELLUM_API_KEY" in result.output


@patch("subprocess.run")
@patch("docker.from_env")
def test_image_push_docker_service_token_500_error(mock_docker_from_env, mock_run, vellum_client, monkeypatch):
    monkeypatch.setenv("VELLUM_API_URL", "https://api.vellum.ai")
    monkeypatch.setenv("VELLUM_API_KEY", "123456abcdef")

    mock_docker_client = mock_docker_from_env.return_value
    mock_docker_client.images.get.return_value.id = "test-image-id"

    mock_run.side_effect = [
        subprocess.CompletedProcess(
            args="", returncode=0, stdout=b'{"manifests": [{"platform": {"architecture": "amd64"}}]}'
        ),
    ]

    vellum_client.container_images.docker_service_token.side_effect = ApiError(
        status_code=500, body="Internal Server Error"
    )

    runner = CliRunner()
    result = runner.invoke(cli_main, ["image", "push", "myimage:latest"])

    assert result.exit_code == 1
    assert "Server error" in result.output
    assert "try again later" in result.output


@patch("subprocess.run")
@patch("docker.from_env")
def test_image_push_docker_service_token_other_error(mock_docker_from_env, mock_run, vellum_client, monkeypatch):
    monkeypatch.setenv("VELLUM_API_URL", "https://api.vellum.ai")
    monkeypatch.setenv("VELLUM_API_KEY", "123456abcdef")

    mock_docker_client = mock_docker_from_env.return_value
    mock_docker_client.images.get.return_value.id = "test-image-id"

    mock_run.side_effect = [
        subprocess.CompletedProcess(
            args="", returncode=0, stdout=b'{"manifests": [{"platform": {"architecture": "amd64"}}]}'
        ),
    ]

    vellum_client.container_images.docker_service_token.side_effect = ApiError(
        status_code=429, body="Too Many Requests"
    )

    runner = CliRunner()
    result = runner.invoke(cli_main, ["image", "push", "myimage:latest"])

    assert result.exit_code == 1
    assert "API request failed" in result.output
    assert "HTTP 429" in result.output


@patch("subprocess.run")
@patch("docker.from_env")
def test_image_push_container_image_401_error(mock_docker_from_env, mock_run, vellum_client, monkeypatch):
    monkeypatch.setenv("VELLUM_API_URL", "https://api.vellum.ai")
    monkeypatch.setenv("VELLUM_API_KEY", "123456abcdef")

    mock_docker_client = mock_docker_from_env.return_value
    mock_docker_client.images.get.return_value.id = "test-image-id"
    mock_docker_client.images.push.return_value = ["pushed"]

    mock_run.side_effect = [
        subprocess.CompletedProcess(
            args="", returncode=0, stdout=b'{"manifests": [{"platform": {"architecture": "amd64"}}]}'
        ),
        subprocess.CompletedProcess(args="", returncode=0, stdout=b'[{"RepoDigests": ["test-repo@sha256:abcd1234"]}]'),
    ]

    vellum_client.container_images.docker_service_token.return_value = type(
        "obj", (object,), {"access_token": "345678mnopqr", "organization_id": str(uuid4()), "repository": "myrepo.net"}
    )()

    vellum_client.container_images.push_container_image.side_effect = ApiError(status_code=401, body="Unauthorized")

    runner = CliRunner()
    result = runner.invoke(cli_main, ["image", "push", "myimage:latest"])

    assert result.exit_code == 1
    assert "Authentication failed" in result.output
    assert "VELLUM_API_KEY" in result.output


@patch("subprocess.run")
@patch("docker.from_env")
def test_image_push_container_image_500_error(mock_docker_from_env, mock_run, vellum_client, monkeypatch):
    monkeypatch.setenv("VELLUM_API_URL", "https://api.vellum.ai")
    monkeypatch.setenv("VELLUM_API_KEY", "123456abcdef")

    mock_docker_client = mock_docker_from_env.return_value
    mock_docker_client.images.get.return_value.id = "test-image-id"
    mock_docker_client.images.push.return_value = ["pushed"]

    mock_run.side_effect = [
        subprocess.CompletedProcess(
            args="", returncode=0, stdout=b'{"manifests": [{"platform": {"architecture": "amd64"}}]}'
        ),
        subprocess.CompletedProcess(args="", returncode=0, stdout=b'[{"RepoDigests": ["test-repo@sha256:abcd1234"]}]'),
    ]

    vellum_client.container_images.docker_service_token.return_value = type(
        "obj", (object,), {"access_token": "345678mnopqr", "organization_id": str(uuid4()), "repository": "myrepo.net"}
    )()

    vellum_client.container_images.push_container_image.side_effect = ApiError(
        status_code=500, body="Internal Server Error"
    )

    runner = CliRunner()
    result = runner.invoke(cli_main, ["image", "push", "myimage:latest"])

    assert result.exit_code == 1
    assert "Server error" in result.output
    assert "try again later" in result.output


@patch("subprocess.run")
@patch("docker.from_env")
def test_image_push_container_image_other_error(mock_docker_from_env, mock_run, vellum_client, monkeypatch):
    monkeypatch.setenv("VELLUM_API_URL", "https://api.vellum.ai")
    monkeypatch.setenv("VELLUM_API_KEY", "123456abcdef")

    mock_docker_client = mock_docker_from_env.return_value
    mock_docker_client.images.get.return_value.id = "test-image-id"
    mock_docker_client.images.push.return_value = ["pushed"]

    mock_run.side_effect = [
        subprocess.CompletedProcess(
            args="", returncode=0, stdout=b'{"manifests": [{"platform": {"architecture": "amd64"}}]}'
        ),
        subprocess.CompletedProcess(args="", returncode=0, stdout=b'[{"RepoDigests": ["test-repo@sha256:abcd1234"]}]'),
    ]

    vellum_client.container_images.docker_service_token.return_value = type(
        "obj", (object,), {"access_token": "345678mnopqr", "organization_id": str(uuid4()), "repository": "myrepo.net"}
    )()

    vellum_client.container_images.push_container_image.side_effect = ApiError(
        status_code=429, body="Too Many Requests"
    )

    runner = CliRunner()
    result = runner.invoke(cli_main, ["image", "push", "myimage:latest"])

    assert result.exit_code == 1
    assert "API request failed" in result.output
    assert "HTTP 429" in result.output
