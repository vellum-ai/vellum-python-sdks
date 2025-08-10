from functools import cached_property
from queue import Queue
from uuid import uuid4
from typing import TYPE_CHECKING, Dict, List, Optional, Type

from vellum import Vellum
from vellum.workflows.context import ExecutionContext, get_execution_context
from vellum.workflows.events.types import ExternalParentContext
from vellum.workflows.nodes.mocks import MockNodeExecution, MockNodeExecutionArg
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.vellum_client import create_vellum_client

if TYPE_CHECKING:
    from vellum.workflows.events.workflow import WorkflowEvent


class WorkflowContext:
    def __init__(
        self,
        *,
        vellum_client: Optional[Vellum] = None,
        execution_context: Optional[ExecutionContext] = None,
        generated_files: Optional[dict[str, str]] = None,
    ):
        self._vellum_client = vellum_client
        self._event_queue: Optional[Queue["WorkflowEvent"]] = None
        self._node_output_mocks_map: Dict[Type[BaseOutputs], List[MockNodeExecution]] = {}
        self._execution_context = get_execution_context()

        if execution_context is not None:
            self._execution_context.trace_id = execution_context.trace_id
            if execution_context.parent_context is not None:
                self._execution_context.parent_context = execution_context.parent_context

        if self._execution_context.parent_context is None:
            self._execution_context.parent_context = ExternalParentContext(span_id=uuid4())

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
    def node_output_mocks_map(self) -> Dict[Type[BaseOutputs], List[MockNodeExecution]]:
        return self._node_output_mocks_map

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

    def _emit_subworkflow_event(self, event: "WorkflowEvent") -> None:
        if self._event_queue:
            self._event_queue.put(event)

    def _register_event_queue(self, event_queue: Queue["WorkflowEvent"]) -> None:
        self._event_queue = event_queue

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

    @classmethod
    def create_from(cls, context):
        return cls(vellum_client=context.vellum_client, generated_files=context.generated_files)
