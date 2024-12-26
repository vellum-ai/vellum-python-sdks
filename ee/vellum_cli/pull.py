import io
import os
from pathlib import Path
from uuid import UUID
import zipfile
from typing import Optional, Union

from dotenv import load_dotenv
from pydash import snake_case

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.vellum_client import create_vellum_client
from vellum_cli.config import VellumCliConfig, WorkflowConfig, load_vellum_cli_config
from vellum_cli.logger import load_cli_logger

ERROR_LOG_FILE_NAME = "error.log"


def _is_valid_uuid(val: Union[str, UUID, None]) -> bool:
    try:
        UUID(str(val))
        return True
    except (ValueError, TypeError):
        return False


class WorkflowConfigResolutionResult(UniversalBaseModel):
    workflow_config: Optional[WorkflowConfig] = None
    pk: Optional[str] = None


def _resolve_workflow_config(
    config: VellumCliConfig,
    module: Optional[str] = None,
    workflow_sandbox_id: Optional[str] = None,
    workflow_deployment: Optional[str] = None,
) -> WorkflowConfigResolutionResult:
    if workflow_sandbox_id and workflow_deployment:
        raise ValueError("Cannot specify both workflow_sandbox_id and workflow_deployment")

    if module:
        workflow_config = next((w for w in config.workflows if w.module == module), None)
        return WorkflowConfigResolutionResult(
            workflow_config=workflow_config,
            pk=workflow_config.workflow_sandbox_id if workflow_config else None,
        )
    elif workflow_sandbox_id:
        workflow_config = WorkflowConfig(
            workflow_sandbox_id=workflow_sandbox_id,
            module=f"workflow_{workflow_sandbox_id.split('-')[0]}",
        )
        config.workflows.append(workflow_config)
        return WorkflowConfigResolutionResult(
            workflow_config=workflow_config,
            pk=workflow_config.workflow_sandbox_id,
        )
    elif workflow_deployment:
        module = (
            f"workflow_{workflow_deployment.split('-')[0]}"
            if _is_valid_uuid(workflow_deployment)
            else snake_case(workflow_deployment)
        )
        workflow_config = WorkflowConfig(
            module=module,
        )
        config.workflows.append(workflow_config)
        return WorkflowConfigResolutionResult(
            workflow_config=workflow_config,
            pk=workflow_deployment,
        )
    elif config.workflows:
        return WorkflowConfigResolutionResult(
            workflow_config=config.workflows[0],
            pk=config.workflows[0].workflow_sandbox_id,
        )

    return WorkflowConfigResolutionResult()


def pull_command(
    module: Optional[str] = None,
    workflow_sandbox_id: Optional[str] = None,
    workflow_deployment: Optional[str] = None,
    include_json: Optional[bool] = None,
    exclude_code: Optional[bool] = None,
    strict: Optional[bool] = None,
    include_sandbox: Optional[bool] = None,
) -> None:
    load_dotenv()
    logger = load_cli_logger()
    config = load_vellum_cli_config()

    workflow_config_result = _resolve_workflow_config(
        config=config,
        module=module,
        workflow_sandbox_id=workflow_sandbox_id,
        workflow_deployment=workflow_deployment,
    )
    save_lock_file = not module

    workflow_config = workflow_config_result.workflow_config
    if not workflow_config:
        raise ValueError("No workflow config found in project to pull from.")

    pk = workflow_config_result.pk
    if not pk:
        raise ValueError("No workflow sandbox ID found in project to pull from.")

    logger.info(f"Pulling workflow into {workflow_config.module}")
    client = create_vellum_client()
    query_parameters = {}
    if include_json:
        query_parameters["include_json"] = include_json
    if exclude_code:
        query_parameters["exclude_code"] = exclude_code
    if strict:
        query_parameters["strict"] = strict
    if include_sandbox:
        query_parameters["include_sandbox"] = include_sandbox

    response = client.workflows.pull(
        pk,
        request_options={"additional_query_parameters": query_parameters},
    )

    zip_bytes = b"".join(response)
    zip_buffer = io.BytesIO(zip_bytes)

    target_dir = os.path.join(os.getcwd(), *workflow_config.module.split("."))
    error_content = ""
    with zipfile.ZipFile(zip_buffer) as zip_file:
        # Delete files in target_dir that aren't in the zip file
        if os.path.exists(target_dir):
            ignore_patterns = (
                workflow_config.ignore
                if isinstance(workflow_config.ignore, list)
                else [workflow_config.ignore] if isinstance(workflow_config.ignore, str) else []
            )
            existing_files = []
            for root, _, files in os.walk(target_dir):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), target_dir)
                    existing_files.append(rel_path)

            for file in existing_files:
                if any(Path(file).match(ignore_pattern) for ignore_pattern in ignore_patterns):
                    continue

                if file not in zip_file.namelist():
                    file_path = os.path.join(target_dir, file)
                    logger.info(f"Deleting {file_path}...")
                    os.remove(file_path)

        for file_name in zip_file.namelist():
            target_file = os.path.join(target_dir, file_name)
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            with zip_file.open(file_name) as source, open(target_file, "w") as target:
                content = source.read().decode("utf-8")
                if file_name == ERROR_LOG_FILE_NAME:
                    error_content = content
                    continue

                logger.info(f"Writing to {target_file}...")
                target.write(content)

    if include_json:
        logger.warning(
            """The pulled JSON representation of the Workflow should be used for debugging purposely only. \
Its schema should be considered unstable and subject to change at any time."""
        )

    if include_sandbox:
        if not workflow_config.ignore:
            workflow_config.ignore = "sandbox.py"
            save_lock_file = True
        elif isinstance(workflow_config.ignore, str) and "sandbox.py" != workflow_config.ignore:
            workflow_config.ignore = [workflow_config.ignore, "sandbox.py"]
            save_lock_file = True
        elif isinstance(workflow_config.ignore, list) and "sandbox.py" not in workflow_config.ignore:
            workflow_config.ignore.append("sandbox.py")
            save_lock_file = True

    if save_lock_file:
        config.save()

    if error_content:
        logger.error(error_content)
    else:
        logger.info(f"Successfully pulled Workflow into {workflow_config.module}")
