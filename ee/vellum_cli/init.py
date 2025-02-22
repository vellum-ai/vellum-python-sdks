import io
import json
import os
from pathlib import Path
import zipfile
from typing import Optional

import click
from dotenv import load_dotenv
from pydash import snake_case

from vellum.workflows.vellum_client import create_vellum_client
from vellum_cli.config import WorkflowConfig, load_vellum_cli_config
from vellum_cli.logger import load_cli_logger
from vellum_cli.pull import PullContentsMetadata, WorkflowConfigResolutionResult

ERROR_LOG_FILE_NAME = "error.log"
METADATA_FILE_NAME = "metadata.json"


def init_command():
    load_dotenv()
    logger = load_cli_logger()
    config = load_vellum_cli_config()

    client = create_vellum_client()
    templates_response = client.workflow_sandboxes.list_workflow_sandbox_examples(tag="TEMPLATES")

    templates = templates_response.results
    if not templates:
        logger.error("No templates available")
        return

    click.echo(click.style("Available Templates", bold=True, fg="green"))
    for idx, template in enumerate(templates, 1):
        click.echo(f"{idx}. {template.label}")

    choice = click.prompt(
        f"Please select a template number (1-{len(templates)})", type=click.IntRange(1, len(templates))
    )
    selected_template = templates[choice - 1]

    click.echo(click.style(f"\nYou selected: {selected_template.label}\n", bold=True, fg="cyan"))

    # Create workflow config with module name from template label
    workflow_config = WorkflowConfig(
        workflow_sandbox_id=selected_template.id,
        module=snake_case(selected_template.label),  # Set module name directly from template
    )
    config.workflows.append(workflow_config)

    workflow_config_result = WorkflowConfigResolutionResult(
        workflow_config=workflow_config,
        pk=selected_template.id,
    )

    pk = workflow_config_result.pk
    if not pk:
        raise ValueError("No workflow sandbox ID found in project to pull from.")

    logger.info(f"Pulling workflow into {workflow_config.module}...")

    query_parameters = {
        "include_sandbox": True,
    }

    response = client.workflows.pull(
        pk,
        request_options={"additional_query_parameters": query_parameters},
    )

    zip_bytes = b"".join(response)
    zip_buffer = io.BytesIO(zip_bytes)

    error_content = ""

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

            if not workflow_config.module and pull_contents_metadata.label:
                workflow_config.module = snake_case(pull_contents_metadata.label)

        if not workflow_config.module:
            raise ValueError(f"Failed to resolve a module name for Workflow {pk}")

        target_dir = os.path.join(os.getcwd(), *workflow_config.module.split("."))

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

    config.save()

    if error_content:
        logger.error(error_content)
    else:
        logger.info(f"Successfully pulled Workflow into {target_dir}")
