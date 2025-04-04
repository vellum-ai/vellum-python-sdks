from dotenv import load_dotenv

from vellum.client.core.api_error import ApiError
from vellum.workflows.vellum_client import create_vellum_client
from vellum_cli.logger import load_cli_logger


def ping_command():
    load_dotenv()
    logger = load_cli_logger()

    client = create_vellum_client()

    try:
        workspace = client.workspaces.workspace_identity()
        organization = client.organizations.organization_identity()
    except ApiError as e:
        # If user did not provide an API key, we will get a 403 error
        if e.status_code == 401 or e.status_code == 403:
            raise Exception(
                "Please make sure your `VELLUM_API_KEY` environment variable is set correctly."  # noqa: E501
            ) from e
        raise Exception(
            "The API we tried to ping returned an invalid response. Please make sure your `VELLUM_API_URL` environment variable is set correctly."  # noqa: E501
        )

    logger.info(
        f"""\
Successfully authenticated with Vellum!

Organization:
    ID: {organization.id}
    Name: {organization.name}

Workspace:
    ID: {workspace.id}
    Name: {workspace.name}
"""
    )
