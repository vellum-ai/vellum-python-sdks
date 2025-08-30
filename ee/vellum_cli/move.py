import os
import shutil
from typing import Optional

from dotenv import load_dotenv

from vellum_cli.config import DEFAULT_WORKSPACE_CONFIG, load_vellum_cli_config
from vellum_cli.logger import load_cli_logger
from vellum_cli.push import module_exists


def move_command(
    old_module: str,
    new_module: str,
    workspace: Optional[str] = None,
) -> None:
    load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))
    logger = load_cli_logger()
    config = load_vellum_cli_config()

    if not module_exists(old_module):
        raise ValueError(f"Module '{old_module}' does not exist in the filesystem.")

    if module_exists(new_module):
        raise ValueError(f"Module '{new_module}' already exists. Cannot move to existing module.")

    matching_configs = [w for w in config.workflows if w.module == old_module]

    if workspace:
        matching_configs = [w for w in matching_configs if w.workspace == workspace]
    else:
        matching_configs = [w for w in matching_configs if w.workspace == DEFAULT_WORKSPACE_CONFIG.name]

    if not matching_configs:
        workspace_msg = (
            f" in workspace '{workspace}'" if workspace else f" in workspace '{DEFAULT_WORKSPACE_CONFIG.name}'"
        )
        raise ValueError(f"No workflow configuration found for module '{old_module}'{workspace_msg}.")

    logger.info(f"Moving module from '{old_module}' to '{new_module}'...")

    old_path = os.path.join(os.getcwd(), *old_module.split("."))
    new_path = os.path.join(os.getcwd(), *new_module.split("."))

    os.makedirs(os.path.dirname(new_path), exist_ok=True)

    shutil.move(old_path, new_path)
    logger.info(f"Moved filesystem directory from '{old_path}' to '{new_path}'")

    for workflow_config in matching_configs:
        workflow_config.module = new_module
        logger.info(f"Updated workflow configuration: {workflow_config.workflow_sandbox_id}")

    config.save()
    logger.info("Updated vellum.lock.json file.")
    logger.info(f"Successfully moved module from '{old_module}' to '{new_module}'")
