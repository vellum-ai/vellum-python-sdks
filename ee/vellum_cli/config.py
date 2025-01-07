from dataclasses import field
import json
import os
from uuid import UUID
from typing import Dict, List, Literal, Optional, Union

import tomli

from vellum.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.state.encoder import DefaultStateEncoder

LOCKFILE_PATH = "vellum.lock.json"
PYPROJECT_TOML_PATH = "pyproject.toml"


class WorkflowDeploymentConfig(UniversalBaseModel):
    id: Optional[UUID] = None
    label: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    release_tags: Optional[List[str]] = None

    def merge(self, other: "WorkflowDeploymentConfig") -> "WorkflowDeploymentConfig":
        return WorkflowDeploymentConfig(
            id=self.id or other.id,
            label=self.label or other.label,
            name=self.name or other.name,
            description=self.description or other.description,
            release_tags=self.release_tags or other.release_tags,
        )


class WorkflowConfig(UniversalBaseModel):
    module: str
    workflow_sandbox_id: Optional[str] = None
    ignore: Optional[Union[str, List[str]]] = None
    deployments: List[WorkflowDeploymentConfig] = field(default_factory=list)
    container_image_name: Optional[str] = None
    container_image_tag: Optional[str] = None

    def merge(self, other: "WorkflowConfig") -> "WorkflowConfig":
        self_deployment_by_id = {
            deployment.id: deployment for deployment in self.deployments if deployment.id is not None
        }
        other_deployment_by_id = {
            deployment.id: deployment for deployment in other.deployments if deployment.id is not None
        }
        all_ids = sorted(set(self_deployment_by_id.keys()).union(set(other_deployment_by_id.keys())))
        merged_deployments = []
        for id in all_ids:
            self_deployment = self_deployment_by_id.get(id)
            other_deployment = other_deployment_by_id.get(id)
            if self_deployment and other_deployment:
                merged_deployments.append(self_deployment.merge(other_deployment))
            elif self_deployment:
                merged_deployments.append(self_deployment)
            elif other_deployment:
                merged_deployments.append(other_deployment)

        for deployment in self.deployments:
            if deployment.id is None:
                merged_deployments.append(deployment)

        for deployment in other.deployments:
            if deployment.id is None:
                merged_deployments.append(deployment)

        return WorkflowConfig(
            module=self.module,
            workflow_sandbox_id=self.workflow_sandbox_id or other.workflow_sandbox_id,
            ignore=self.ignore or other.ignore,
            deployments=merged_deployments,
            container_image_tag=self.container_image_tag or other.container_image_tag,
            container_image_name=self.container_image_name or other.container_image_name,
        )


class VellumCliConfig(UniversalBaseModel):
    version: Literal["1.0"] = "1.0"
    workflows: List[WorkflowConfig] = field(default_factory=list)

    def save(self) -> None:
        lockfile_path = os.path.join(os.getcwd(), LOCKFILE_PATH)
        with open(lockfile_path, "w") as f:
            json.dump(self.model_dump(), f, indent=2, cls=DefaultStateEncoder)

    def merge(self, other: "VellumCliConfig") -> "VellumCliConfig":
        if other.version != self.version:
            raise ValueError("Lockfile version mismatch")

        self_workflow_by_module = {workflow.module: workflow for workflow in self.workflows}
        other_workflow_by_module = {workflow.module: workflow for workflow in other.workflows}
        all_modules = sorted(set(self_workflow_by_module.keys()).union(set(other_workflow_by_module.keys())))
        merged_workflows = []
        for module in all_modules:
            self_workflow = self_workflow_by_module.get(module)
            other_workflow = other_workflow_by_module.get(module)
            if self_workflow and other_workflow:
                merged_workflows.append(self_workflow.merge(other_workflow))
            elif self_workflow:
                merged_workflows.append(self_workflow)
            elif other_workflow:
                merged_workflows.append(other_workflow)

        return VellumCliConfig(workflows=merged_workflows, version=self.version)


def load_vellum_cli_config(root_dir: Optional[str] = None) -> VellumCliConfig:
    if root_dir is None:
        root_dir = os.getcwd()
    lockfile_path = os.path.join(root_dir, LOCKFILE_PATH)
    if not os.path.exists(lockfile_path):
        lockfile_data = {}
    else:
        with open(lockfile_path, "rb") as f:
            lockfile_data = json.load(f)
    lockfile_config = VellumCliConfig.model_validate(lockfile_data)

    pyproject_toml_path = os.path.join(root_dir, PYPROJECT_TOML_PATH)
    if not os.path.exists(pyproject_toml_path):
        toml_vellum: Dict = {}
    else:
        with open(pyproject_toml_path, "rb") as f:
            toml_loaded = tomli.load(f)
        toml_tool = toml_loaded.get("tool", {})
        if not isinstance(toml_tool, dict):
            toml_vellum = {}

        toml_vellum = toml_tool.get("vellum")
        if not isinstance(toml_vellum, dict):
            # Mypy is wrong. this is totally reachable.
            toml_vellum = {}  # type: ignore[unreachable]
    toml_config = VellumCliConfig.model_validate(toml_vellum)

    return toml_config.merge(lockfile_config)
