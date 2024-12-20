from importlib import metadata
import io
import json
import os
import sys
import tarfile
from uuid import UUID
from typing import List, Optional

from dotenv import load_dotenv

from vellum.resources.workflows.client import OMIT
from vellum.types import WorkflowPushDeploymentConfigRequest
from vellum.workflows.utils.names import snake_to_title_case
from vellum.workflows.vellum_client import create_vellum_client
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_cli.config import WorkflowDeploymentConfig, load_vellum_cli_config
from vellum_cli.logger import load_cli_logger
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay


def push_command(
    module: Optional[str] = None,
    deploy: Optional[bool] = None,
    deployment_label: Optional[str] = None,
    deployment_name: Optional[str] = None,
    deployment_description: Optional[str] = None,
    release_tags: Optional[List[str]] = None,
) -> None:
    load_dotenv()
    logger = load_cli_logger()
    config = load_vellum_cli_config()

    if not config.workflows:
        raise ValueError("No Workflows found in project to push.")

    if len(config.workflows) > 1 and not module:
        raise ValueError("Multiple workflows found in project to push. Pushing only a single workflow is supported.")

    workflow_config = next((w for w in config.workflows if w.module == module), None) if module else config.workflows[0]
    if workflow_config is None:
        raise ValueError(f"No workflow config for '{module}' found in project to push.")

    logger.info(f"Loading workflow from {workflow_config.module}")
    client = create_vellum_client()
    sys.path.insert(0, os.getcwd())

    # Remove this once we could serialize using the artifact in Vembda
    # https://app.shortcut.com/vellum/story/5585
    workflow = BaseWorkflow.load_from_module(workflow_config.module)
    workflow_display = get_workflow_display(base_display_class=VellumWorkflowDisplay, workflow_class=workflow)
    exec_config = workflow_display.serialize()
    exec_config["runner_config"] = {
        "sdk_version": metadata.version("vellum-ai"),
    }

    label = snake_to_title_case(workflow_config.module.split(".")[-1])

    deployment_config: WorkflowPushDeploymentConfigRequest = OMIT
    deployment_config_serialized: str = OMIT
    if deploy:
        cli_deployment_config = (
            workflow_config.deployments[0] if workflow_config.deployments else WorkflowDeploymentConfig()
        )

        deployment_config = WorkflowPushDeploymentConfigRequest(
            label=deployment_label or cli_deployment_config.label,
            name=deployment_name or cli_deployment_config.name,
            description=deployment_description or cli_deployment_config.description,
            release_tags=release_tags or cli_deployment_config.release_tags,
        )

        # We should check with fern if we could auto-serialize typed fields for us
        # https://app.shortcut.com/vellum/story/5568
        deployment_config_serialized = json.dumps({k: v for k, v in deployment_config.dict().items() if v is not None})

    artifact = io.BytesIO()
    with tarfile.open(fileobj=artifact, mode="w:gz") as tar:
        module_dir = workflow_config.module.replace(".", os.path.sep)
        for root, _, files in os.walk(module_dir):
            for filename in files:
                if not filename.endswith(".py"):
                    continue

                file_path = os.path.join(root, filename)
                # Get path relative to module_dir for tar archive
                relative_path = os.path.relpath(file_path, module_dir)
                content_bytes = open(file_path, "rb").read()
                file_buffer = io.BytesIO(content_bytes)

                tarinfo = tarfile.TarInfo(name=relative_path)
                tarinfo.size = len(content_bytes)

                tar.addfile(tarinfo, file_buffer)

    artifact.seek(0)
    artifact.name = f"{workflow_config.module.replace('.', '__')}.tar.gz"

    response = client.workflows.push(
        # Remove this once we could serialize using the artifact in Vembda
        # https://app.shortcut.com/vellum/story/5585
        exec_config=json.dumps(exec_config),
        label=label,
        workflow_sandbox_id=workflow_config.workflow_sandbox_id,
        artifact=artifact,
        # We should check with fern if we could auto-serialize typed object fields for us
        # https://app.shortcut.com/vellum/story/5568
        deployment_config=deployment_config_serialized,  # type: ignore[arg-type]
    )
    logger.info(
        f"""Successfully pushed {label} to Vellum!
Visit at: https://app.vellum.ai/workflow-sandboxes/{response.workflow_sandbox_id}"""
    )

    requires_save = False
    if not workflow_config.workflow_sandbox_id:
        workflow_config.workflow_sandbox_id = response.workflow_sandbox_id
        requires_save = True

    if not workflow_config.deployments and response.workflow_deployment_id:
        workflow_config.deployments.append(WorkflowDeploymentConfig(id=UUID(response.workflow_deployment_id)))
        requires_save = True

    if requires_save:
        config.save()
        logger.info("Updated vellum.lock file.")
