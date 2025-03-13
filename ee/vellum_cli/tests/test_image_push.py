import subprocess
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from vellum_cli import main as cli_main


@patch("subprocess.run")
@patch("docker.from_env")
def test_image_push__self_hosted_happy_path(mock_docker_from_env, mock_run, vellum_client, monkeypatch):
    # GIVEN a self hosted vellum api URL env var
    monkeypatch.setenv("VELLUM_API_URL", "mycompany.api.com")

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
