from dotenv import load_dotenv

from vellum.workflows.vellum_client import create_vellum_client
from vellum_cli.logger import load_cli_logger


def ping_command():
    load_dotenv()
    logger = load_cli_logger()

    client = create_vellum_client()

    workspace = client.workspaces.workspace_identity()
    organization = client.organizations.organization_identity()

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
