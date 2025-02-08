from importlib import metadata
import io
import json
import os
import sys
import tarfile
from uuid import UUID
from typing import List, Optional

from dotenv import load_dotenv

from vellum.client.core.api_error import ApiError
from vellum.resources.workflows.client import OMIT
from vellum.types import WorkflowPushDeploymentConfigRequest
from vellum.workflows.vellum_client import create_vellum_client
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_cli.config import DEFAULT_WORKSPACE_CONFIG, WorkflowConfig, WorkflowDeploymentConfig, load_vellum_cli_config
from vellum_cli.logger import load_cli_logger
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay


def push_command(
    module: Optional[str] = None,
    workflow_sandbox_id: Optional[str] = None,
    deploy: Optional[bool] = None,
    deployment_label: Optional[str] = None,
    deployment_name: Optional[str] = None,
    deployment_description: Optional[str] = None,
    release_tags: Optional[List[str]] = None,
    dry_run: Optional[bool] = None,
    strict: Optional[bool] = None,
    workspace: Optional[str] = None,
) -> None:
    load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))
    logger = load_cli_logger()
    config = load_vellum_cli_config()

    if not config.workflows:
        raise ValueError("No Workflows found in project to push.")

    workflow_configs = (
        [
            w
            for w in config.workflows
            if (module and w.module == module) or (workflow_sandbox_id and w.workflow_sandbox_id == workflow_sandbox_id)
        ]
        if module or workflow_sandbox_id
        else config.workflows
    )

    if len(workflow_configs) > 1 and workspace:
        workflow_configs = [w for w in workflow_configs if w.workspace == workspace]

    if len(workflow_configs) == 0:
        if module and module_exists(module):
            new_config = WorkflowConfig(
                module=module,
                workflow_sandbox_id=workflow_sandbox_id,
                workspace=workspace or DEFAULT_WORKSPACE_CONFIG.name,
            )
            config.workflows.append(new_config)
            workflow_configs = [new_config]
        else:
            raise ValueError(f"No workflow config for '{module}' found in project to push.")

    if len(workflow_configs) > 1:
        raise ValueError("Multiple workflows found in project to push. Pushing only a single workflow is supported.")

    workflow_config = workflow_configs[0]

    logger.info(f"Loading workflow from {workflow_config.module}")
    resolved_workspace = workspace or workflow_config.workspace or DEFAULT_WORKSPACE_CONFIG.name
    workspace_config = (
        next((w for w in config.workspaces if w.name == resolved_workspace), DEFAULT_WORKSPACE_CONFIG)
        if workspace
        else DEFAULT_WORKSPACE_CONFIG
    )
    api_key = os.getenv(workspace_config.api_key)
    if not api_key:
        raise ValueError(f"No API key value found in environment for workspace '{workspace_config.name}'.")

    if workspace_config.name != workflow_config.workspace:
        # We are pushing to a new workspace, so we need a new workflow config
        workflow_config = WorkflowConfig(
            module=workflow_config.module,
            workspace=workspace_config.name,
        )
        config.workflows.append(workflow_config)

    if (
        workflow_sandbox_id
        and workflow_config.workflow_sandbox_id
        and workflow_config.workflow_sandbox_id != workflow_sandbox_id
    ):
        raise ValueError(
            f"Workflow sandbox id '{workflow_sandbox_id}' is already associated with '{workflow_config.module}'."
        )

    client = create_vellum_client(
        api_key=api_key,
    )
    sys.path.insert(0, os.getcwd())

    # Remove this once we could serialize using the artifact in Vembda
    # https://app.shortcut.com/vellum/story/5585
    workflow = BaseWorkflow.load_from_module(workflow_config.module)
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay,
        workflow_class=workflow,
        dry_run=dry_run or False,
    )
    exec_config = workflow_display.serialize()

    container_tag = workflow_config.container_image_tag
    if workflow_config.container_image_name and not workflow_config.container_image_tag:
        container_tag = "latest"

    exec_config["runner_config"] = {
        "sdk_version": metadata.version("vellum-ai"),
        "container_image_tag": container_tag,
        "container_image_name": workflow_config.container_image_name,
    }

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

    try:
        response = client.workflows.push(
            # Remove this once we could serialize using the artifact in Vembda
            # https://app.shortcut.com/vellum/story/5585
            exec_config=json.dumps(exec_config),
            workflow_sandbox_id=workflow_config.workflow_sandbox_id or workflow_sandbox_id,
            artifact=artifact,
            # We should check with fern if we could auto-serialize typed object fields for us
            # https://app.shortcut.com/vellum/story/5568
            deployment_config=deployment_config_serialized,  # type: ignore[arg-type]
            dry_run=dry_run,
            strict=strict,
        )
    except ApiError as e:
        if e.status_code != 400 or not isinstance(e.body, dict) or "diffs" not in e.body:
            raise e

        diffs: dict = e.body["diffs"]
        generated_only = diffs.get("generated_only", [])
        generated_only_str = (
            "\n".join(
                ["Files that were generated but not found in the original project:"]
                + [f"- {file}" for file in generated_only]
            )
            if generated_only
            else ""
        )

        original_only = diffs.get("original_only", [])
        original_only_str = (
            "\n".join(
                ["Files that were found in the original project but not generated:"]
                + [f"- {file}" for file in original_only]
            )
            if original_only
            else ""
        )

        modified = diffs.get("modified", {})
        modified_str = (
            "\n\n".join(
                ["Files that were different between the original project and the generated artifact:"]
                + ["\n".join(line.strip() for line in lines) for lines in modified.values()]
            )
            if modified
            else ""
        )

        reported_diffs = f"""\
{e.body.get("detail")}

{generated_only_str}

{original_only_str}

{modified_str}
"""
        logger.error(reported_diffs)
        return

    if dry_run:
        error_messages = [str(e) for e in workflow_display.errors]
        error_message = "\n".join(error_messages) if error_messages else "No errors found."
        logger.info(
            f"""\
# Workflow Push Report

## Errors
{error_message}

## Proposed Diffs
{json.dumps(response.proposed_diffs, indent=2)}
"""
        )  # type: ignore[attr-defined]
    else:
        logger.info(
            f"""Successfully pushed {workflow_config.module} to Vellum!
Visit at: https://app.vellum.ai/workflow-sandboxes/{response.workflow_sandbox_id}"""
        )

    if not workflow_config.workflow_sandbox_id:
        workflow_config.workflow_sandbox_id = response.workflow_sandbox_id

    if not workflow_config.deployments and response.workflow_deployment_id:
        workflow_config.deployments.append(WorkflowDeploymentConfig(id=UUID(response.workflow_deployment_id)))

    config.save()
    logger.info("Updated vellum.lock.json file.")


def module_exists(module_name: str) -> bool:
    module_path = os.path.join(os.getcwd(), *module_name.split("."))
    return os.path.exists(module_path) and os.path.isdir(module_path)
