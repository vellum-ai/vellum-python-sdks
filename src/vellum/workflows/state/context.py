from dataclasses import dataclass
from functools import cached_property
import json
import logging
from queue import Queue
import traceback
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type

from vellum import Vellum, __version__
from vellum.client.types import SeverityEnum
from vellum.workflows.context import ExecutionContext, get_execution_context, set_execution_context
from vellum.workflows.events.node import NodeExecutionLogBody, NodeExecutionLogEvent
from vellum.workflows.events.types import ExternalParentContext, NodeParentContext
from vellum.workflows.nodes.mocks import MockNodeExecution, MockNodeExecutionArg
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.state.store import Store
from vellum.workflows.utils.uuids import generate_workflow_deployment_prefix
from vellum.workflows.utils.zip import extract_zip_files
from vellum.workflows.vellum_client import create_vellum_client

if TYPE_CHECKING:
    from vellum.workflows.events.workflow import WorkflowEvent
    from vellum.workflows.state.base import BaseState
    from vellum.workflows.workflows.base import BaseWorkflow

logger = logging.getLogger(__name__)


@dataclass
class WorkflowDeploymentMetadata:
    """Metadata about a workflow deployment needed for parent context construction."""

    deployment_id: UUID
    deployment_name: str
    deployment_history_item_id: UUID
    release_tag_id: UUID
    release_tag_name: str
    workflow_version_id: UUID


class WorkflowContext:
    def __init__(
        self,
        *,
        vellum_client: Optional[Vellum] = None,
        execution_context: Optional[ExecutionContext] = None,
        generated_files: Optional[dict[str, str]] = None,
        namespace: Optional[str] = None,
        store_class: Optional[Type[Store]] = None,
        event_max_size: Optional[int] = None,
    ):
        self._vellum_client = vellum_client
        self._event_queue: Optional[Queue["WorkflowEvent"]] = None
        self._node_output_mocks_map: Dict[Type[BaseOutputs], List[MockNodeExecution]] = {}
        self._execution_context = get_execution_context()
        self._namespace = namespace
        self._store_class = store_class if store_class is not None else Store
        self._event_max_size = event_max_size

        if execution_context is not None:
            self._execution_context.trace_id = execution_context.trace_id
            if execution_context.parent_context is not None:
                self._execution_context.parent_context = execution_context.parent_context

        if self._execution_context.parent_context is None:
            self._execution_context.parent_context = ExternalParentContext(span_id=uuid4())
            # Only generate a new trace_id if one wasn't explicitly provided (i.e., if it's the default zero UUID)
            if self._execution_context.trace_id == UUID("00000000-0000-0000-0000-000000000000"):
                self._execution_context.trace_id = uuid4()
            # Propagate the updated context back to the global execution context
            set_execution_context(self._execution_context)

        self._generated_files = generated_files

    @cached_property
    def vellum_client(self) -> Vellum:
        if self._vellum_client:
            return self._vellum_client

        return create_vellum_client()

    @cached_property
    def execution_context(self) -> ExecutionContext:
        return self._execution_context

    @cached_property
    def generated_files(self) -> Optional[dict[str, str]]:
        return self._generated_files

    @cached_property
    def namespace(self) -> Optional[str]:
        return self._namespace

    @cached_property
    def node_output_mocks_map(self) -> Dict[Type[BaseOutputs], List[MockNodeExecution]]:
        return self._node_output_mocks_map

    @property
    def store_class(self) -> Type[Store]:
        return self._store_class

    @property
    def event_max_size(self) -> Optional[int]:
        return self._event_max_size

    @property
    def monitoring_url(self) -> Optional[str]:
        """
        Get the base monitoring URL for this workflow context.

        Returns the base URL to view executions in Vellum UI.
        """
        # Get UI URL from the Vellum client's API URL
        api_url = self.vellum_client._client_wrapper.get_environment().default
        return self._get_ui_url_from_api_url(api_url)

    def get_monitoring_url(self, span_id: str) -> Optional[str]:
        """
        Generate the monitoring URL for this workflow execution.

        Args:
        span_id: The span ID from the workflow execution result.

        Returns:
        The URL to view execution details in Vellum UI, or None if monitoring is disabled.
        """
        base_url = self.monitoring_url
        if base_url is None:
            return None

        return f"{base_url}/workflows/executions/{span_id}"

    def _get_ui_url_from_api_url(self, api_url: str) -> str:
        """
        Convert an API URL to the corresponding UI URL.

        Args:
        api_url: The API base URL (e.g., https://api.vellum.ai or http://localhost:8000)

        Returns:
        The corresponding UI URL (e.g., https://app.vellum.ai or http://localhost:3000)
        """
        if "localhost" in api_url:
            # For local development: localhost:8000 (API) -> localhost:3000 (UI)
            return api_url.replace(":8000", ":3000")
        elif "api.vellum.ai" in api_url:
            # For production: api.vellum.ai -> app.vellum.ai
            return api_url.replace("api.vellum.ai", "app.vellum.ai")
        else:
            # For custom domains, assume the same pattern: api.* -> app.*
            return api_url.replace("api.", "app.", 1)

    def emit_log_event(
        self,
        severity: SeverityEnum,
        message: str,
        attributes: Optional[Dict[str, Any]] = None,
        exc_info: Optional[bool] = None,
    ) -> None:
        """Emit a log event for a particular node.

        This is in active development and may have breaking changes.
        """
        from vellum.workflows.nodes.bases import BaseNode

        if self._event_queue is None:
            return

        execution_context = get_execution_context()
        parent_context = execution_context.parent_context
        while parent_context:
            if isinstance(parent_context, NodeParentContext):
                break
            parent_context = parent_context.parent

        if not isinstance(parent_context, NodeParentContext):
            return

        try:
            node_class = parent_context.node_definition.decode()
        except Exception:
            logger.exception("Failed to decode node definition.")
            return

        if not isinstance(node_class, type) or not issubclass(node_class, BaseNode):
            logger.warning("Node definition is not a subclass of BaseNode.")
            return

        if exc_info:
            attributes = {
                **(attributes or {}),
                "exc_info": traceback.format_exc(),
            }

        self._event_queue.put(
            NodeExecutionLogEvent(
                trace_id=execution_context.trace_id,
                span_id=parent_context.span_id,
                body=NodeExecutionLogBody(
                    node_definition=node_class,
                    severity=severity,
                    message=message,
                    attributes=attributes,
                ),
            )
        )

    def _emit_subworkflow_event(self, event: "WorkflowEvent") -> None:
        if self._event_queue:
            self._event_queue.put(event)

    def _register_event_queue(self, event_queue: Queue["WorkflowEvent"]) -> None:
        self._event_queue = event_queue

    def _register_event_max_size(self, event_max_size: Optional[int]) -> None:
        self._event_max_size = event_max_size

    def _register_node_output_mocks(self, node_output_mocks: MockNodeExecutionArg) -> None:
        for mock in node_output_mocks:
            if isinstance(mock, MockNodeExecution):
                key = mock.then_outputs.__class__
                value = mock
            else:
                key = mock.__class__
                value = MockNodeExecution(
                    when_condition=ConstantValueReference(True),
                    then_outputs=mock,
                )

            if key not in self._node_output_mocks_map:
                self._node_output_mocks_map[key] = [value]
            else:
                self._node_output_mocks_map[key].append(value)

    def _get_all_node_output_mocks(self) -> List[MockNodeExecution]:
        return [mock for mocks in self._node_output_mocks_map.values() for mock in mocks]

    def resolve_workflow_deployment(
        self, deployment_name: str, release_tag: str, state: "BaseState"
    ) -> Optional[Tuple[Type["BaseWorkflow"], Optional[WorkflowDeploymentMetadata]]]:
        """
        Resolve a workflow deployment by name and release tag.

        Args:
            deployment_name: The name of the workflow deployment
            release_tag: The release tag to resolve
            state: The base state to pass to the workflow

        Returns:
            Tuple of (BaseWorkflow class, deployment metadata) if found
        """
        if not self._generated_files or not self._namespace:
            return None

        expected_prefix = generate_workflow_deployment_prefix(deployment_name, release_tag)
        WorkflowClass: Optional[Type["BaseWorkflow"]] = None

        try:
            from vellum.workflows.workflows.base import BaseWorkflow

            WorkflowClass = BaseWorkflow.load_from_module(f"{self.namespace}.{expected_prefix}")
            WorkflowClass.is_dynamic = True
        except Exception:
            pass

        if WorkflowClass is None:
            try:
                major_version = __version__.split(".")[0]
                version_range = f">={major_version}.0.0,<={__version__}"

                response = self.vellum_client.workflows.pull(
                    deployment_name,
                    release_tag=release_tag,
                    version=version_range,
                    request_options={"additional_headers": {"X-Vellum-Always-Success": "true"}},
                )

                if isinstance(response, dict) and response.get("success") is False:
                    return None

                zip_bytes = b"".join(response)
                pulled_files = extract_zip_files(zip_bytes)

                for file_name, content in pulled_files.items():
                    prefixed_file_name = f"{expected_prefix}/{file_name}"
                    self._generated_files[prefixed_file_name] = content

                from vellum.workflows.workflows.base import BaseWorkflow

                WorkflowClass = BaseWorkflow.load_from_module(f"{self.namespace}.{expected_prefix}")
                WorkflowClass.is_dynamic = True

            except Exception:
                pass

        # If we successfully loaded the workflow class, fetch metadata from generated_files (important-comment)
        # This ensures we pick up metadata.json if a pull just populated it
        if WorkflowClass is not None:
            deployment_metadata = self._fetch_deployment_metadata(deployment_name, release_tag)
            return (WorkflowClass, deployment_metadata)

        return None

    def _fetch_deployment_metadata(
        self, deployment_name: str, release_tag: str
    ) -> Optional[WorkflowDeploymentMetadata]:
        """
        Fetch deployment metadata from metadata.json in generated_files.

        Args:
            deployment_name: The name of the workflow deployment
            release_tag: The release tag name

        Returns:
            WorkflowDeploymentMetadata if successful, None otherwise
        """
        if not self._generated_files:
            return None

        expected_prefix = generate_workflow_deployment_prefix(deployment_name, release_tag)
        metadata_path = f"{expected_prefix}/metadata.json"

        metadata_content = self._generated_files.get(metadata_path)
        if metadata_content:
            try:
                metadata_json = json.loads(metadata_content)

                deployment_id = metadata_json.get("deployment_id")
                deployment_name_from_metadata = metadata_json.get("deployment_name")
                deployment_history_item_id = metadata_json.get("deployment_history_item_id")
                release_tag_id = metadata_json.get("release_tag_id")
                release_tag_name_from_metadata = metadata_json.get("release_tag_name")
                workflow_version_id = metadata_json.get("workflow_version_id")

                if all(
                    [
                        deployment_id,
                        deployment_name_from_metadata,
                        deployment_history_item_id,
                        release_tag_id,
                        release_tag_name_from_metadata,
                        workflow_version_id,
                    ]
                ):
                    return WorkflowDeploymentMetadata(
                        deployment_id=UUID(deployment_id),
                        deployment_name=deployment_name_from_metadata,
                        deployment_history_item_id=UUID(deployment_history_item_id),
                        release_tag_id=UUID(release_tag_id),
                        release_tag_name=release_tag_name_from_metadata,
                        workflow_version_id=UUID(workflow_version_id),
                    )
            except (json.JSONDecodeError, ValueError, KeyError):
                # If we fail to parse metadata, return None - the workflow can still run
                # but won't have the full parent context hierarchy
                pass

        return None

    @classmethod
    def create_from(cls, context: "WorkflowContext") -> "WorkflowContext":
        return cls(
            vellum_client=context.vellum_client,
            generated_files=context.generated_files,
            namespace=context.namespace,
            store_class=context.store_class,
            event_max_size=context.event_max_size,
        )
