import io
import json
import os
from pathlib import Path
import zipfile
from typing import Optional

from dotenv import load_dotenv
from pydash import snake_case

from vellum.client.core.api_error import ApiError
from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.vellum_client import create_vellum_client
from vellum_cli.config import VellumCliConfig, WorkflowConfig, load_vellum_cli_config
from vellum_cli.logger import load_cli_logger

ERROR_LOG_FILE_NAME = "error.log"
METADATA_FILE_NAME = "metadata.json"


class WorkflowConfigResolutionResult(UniversalBaseModel):
    workflow_config: Optional[WorkflowConfig] = None
    pk: Optional[str] = None


class RunnerConfig(UniversalBaseModel):
    container_image_name: Optional[str] = None
    container_image_tag: Optional[str] = None


class PullContentsMetadata(UniversalBaseModel):
    label: Optional[str] = None
    runner_config: Optional[RunnerConfig] = None
    deployment_name: Optional[str] = None


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
        if not workflow_config and workflow_sandbox_id:
            workflow_config = WorkflowConfig(
                workflow_sandbox_id=workflow_sandbox_id,
                module=module,
            )
            config.workflows.append(workflow_config)
            return WorkflowConfigResolutionResult(
                workflow_config=workflow_config,
                pk=workflow_sandbox_id,
            )

        return WorkflowConfigResolutionResult(
            workflow_config=workflow_config,
            pk=workflow_config.workflow_sandbox_id if workflow_config else None,
        )
    elif workflow_sandbox_id:
        workflow_config = next((w for w in config.workflows if w.workflow_sandbox_id == workflow_sandbox_id), None)
        if workflow_config:
            return WorkflowConfigResolutionResult(
                workflow_config=workflow_config,
                pk=workflow_sandbox_id,
            )

        # We use an empty module name to indicate that we want to backfill it once we have the Workflow Sandbox Label
        workflow_config = WorkflowConfig(
            workflow_sandbox_id=workflow_sandbox_id,
            module="",
        )
        config.workflows.append(workflow_config)
        return WorkflowConfigResolutionResult(
            workflow_config=workflow_config,
            pk=workflow_config.workflow_sandbox_id,
        )
    elif workflow_deployment:
        workflow_config = WorkflowConfig(
            module="",
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
    target_directory: Optional[str] = None,
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

    workflow_config = workflow_config_result.workflow_config
    if not workflow_config:
        raise ValueError("No workflow config found in project to pull from.")

    pk = workflow_config_result.pk
    if not pk:
        raise ValueError("No workflow sandbox ID found in project to pull from.")

    if workflow_config.module:
        logger.info(f"Pulling workflow {workflow_config.module}...")
    else:
        logger.info(f"Pulling workflow from {pk}...")

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

    try:
        zip_bytes = b"".join(response)
    except ApiError as e:
        if e.status_code == 401 or e.status_code == 403:
            raise Exception("Please make sure your `VELLUM_API_KEY` environment variable is set correctly.")
        raise Exception(
            "The API we tried to pull is invalid. Please make sure your `VELLUM_API_URL` environment variable is set correctly."  # noqa: E501
        )

    zip_buffer = io.BytesIO(zip_bytes)
    error_content = ""
    try:
        with zipfile.ZipFile(zip_buffer) as zip_file:
            if METADATA_FILE_NAME in zip_file.namelist():
                metadata_json: Optional[dict] = None
                with zip_file.open(METADATA_FILE_NAME) as source:
                    metadata_json = json.load(source)

                pull_contents_metadata = PullContentsMetadata.model_validate(metadata_json)

                if pull_contents_metadata.runner_config:
                    workflow_config.container_image_name = pull_contents_metadata.runner_config.container_image_name
                    workflow_config.container_image_tag = pull_contents_metadata.runner_config.container_image_tag
                    if workflow_config.container_image_name and not workflow_config.container_image_tag:
                        workflow_config.container_image_tag = "latest"
                if not workflow_config.module and workflow_deployment and pull_contents_metadata.deployment_name:
                    workflow_config.module = snake_case(pull_contents_metadata.deployment_name)
                if not workflow_config.module and pull_contents_metadata.label:
                    workflow_config.module = snake_case(pull_contents_metadata.label)

            if not workflow_config.module:
                raise ValueError(f"Failed to resolve a module name for Workflow {pk}")

            # Use target_directory if provided, otherwise use current working directory
            base_dir = os.path.join(os.getcwd(), target_directory) if target_directory else os.getcwd()
            target_dir = os.path.join(base_dir, *workflow_config.module.split("."))
            workflow_config.target_directory = target_dir if target_directory else None

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
                with zip_file.open(file_name) as source:
                    content = source.read().decode("utf-8")
                    if file_name == ERROR_LOG_FILE_NAME:
                        error_content = content
                        continue
                    if file_name == METADATA_FILE_NAME:
                        continue

                    target_file = os.path.join(target_dir, file_name)
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    with open(target_file, "w") as target:
                        logger.info(f"Writing to {target_file}...")
                        target.write(content)
    except zipfile.BadZipFile:
        raise Exception(
            "The API we tried to pull from returned an invalid zip file. Please make sure your `VELLUM_API_URL` environment variable is set correctly."  # noqa: E501
        )

    if include_json:
        logger.warning(
            """The pulled JSON representation of the Workflow should be used for debugging purposely only. \
Its schema should be considered unstable and subject to change at any time."""
        )

    if include_sandbox:
        if not workflow_config.ignore:
            workflow_config.ignore = "sandbox.py"
        elif isinstance(workflow_config.ignore, str) and "sandbox.py" != workflow_config.ignore:
            workflow_config.ignore = [workflow_config.ignore, "sandbox.py"]
        elif isinstance(workflow_config.ignore, list) and "sandbox.py" not in workflow_config.ignore:
            workflow_config.ignore.append("sandbox.py")

    config.save()

    if error_content:
        logger.error(error_content)
    else:
        logger.info(f"Successfully pulled Workflow into {target_dir}")
