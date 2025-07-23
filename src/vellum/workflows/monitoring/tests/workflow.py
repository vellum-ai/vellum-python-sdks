"""Simple workflow for testing monitoring decorators - Production-style setup."""

import inspect
from typing import Any, List, Type

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.monitoring.decorators import MonitorDecorator
from vellum.workflows.nodes import MapNode
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    fruits: List[str]


class Iteration(BaseNode):
    item = MapNode.SubworkflowInputs.item
    index = MapNode.SubworkflowInputs.index

    class Outputs(BaseOutputs):
        count: int

    def run(self) -> Outputs:
        return self.Outputs(count=len(self.item) + self.index)


class IterationSubworkflow(BaseWorkflow[MapNode.SubworkflowInputs, BaseState]):
    graph = Iteration

    class Outputs(BaseOutputs):
        count = Iteration.Outputs.count


class MapFruitsNode(MapNode):
    items = Inputs.fruits
    subworkflow = IterationSubworkflow


class SimpleMapExample(BaseWorkflow[Inputs, BaseState]):
    graph = MapFruitsNode
    _monitoring_initialized = False  # Class-level flag for the entire workflow system

    class Outputs(BaseOutputs):
        final_value = MapFruitsNode.Outputs.count

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Production-style: Top-level workflow initializes monitoring for all components
        if not SimpleMapExample._monitoring_initialized:
            self._initialize_monitoring_dynamic()
            SimpleMapExample._monitoring_initialized = True

    def _initialize_monitoring_dynamic(self):
        """Dynamically discover and wrap all execution methods with proper type classification. -- TESTING ONLY."""

        # Classes to monitor with their proper types
        workflow_classes = [SimpleMapExample, IterationSubworkflow]
        node_classes = [MapFruitsNode, Iteration]

        wrapped_methods = set()

        # Wrap workflow classes
        for workflow_class in workflow_classes:
            for method_name in self._get_execution_methods(workflow_class):
                if hasattr(workflow_class, method_name):
                    method = getattr(workflow_class, method_name)
                    if callable(method) and not hasattr(method, "__wrapped__"):
                        monitor_name = f"{workflow_class.__name__}.{method_name}"

                        # Create a monitoring decorator with proper type classification
                        decorator = self._create_workflow_monitor(monitor_name)
                        wrapped_method = decorator(method)
                        setattr(workflow_class, method_name, wrapped_method)
                        wrapped_methods.add(monitor_name)

        # Wrap node classes
        for node_class in node_classes:
            for method_name in self._get_execution_methods(node_class):
                if hasattr(node_class, method_name):
                    method = getattr(node_class, method_name)
                    if callable(method) and not hasattr(method, "__wrapped__"):
                        monitor_name = f"{node_class.__name__}.{method_name}"

                        # Create a monitoring decorator with proper type classification
                        decorator = self._create_node_monitor(monitor_name)
                        wrapped_method = decorator(method)
                        setattr(node_class, method_name, wrapped_method)
                        wrapped_methods.add(monitor_name)

        # Successfully wrapped all discovered execution methods

    def _get_execution_methods(self, cls: Type[Any]) -> List[str]:
        """Get list of methods that should be monitored for a class."""
        execution_methods = []

        # Standard execution methods
        standard_methods = ["run", "stream", "_run_subworkflow", "_context_run_subworkflow"]

        for method_name in standard_methods:
            if hasattr(cls, method_name):
                method = getattr(cls, method_name)
                if callable(method) and not method_name.startswith("__"):
                    execution_methods.append(method_name)

        # Find any additional methods that look like execution methods
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if (
                name.endswith("_execution")
                or name.startswith("execute_")
                or name.endswith("_run")
                or name.startswith("run_")
            ):
                if name not in execution_methods:
                    execution_methods.append(name)

        return execution_methods

    def _create_workflow_monitor(self, name: str):
        """Create a monitoring decorator that forces WORKFLOW type."""

        class WorkflowMonitorDecorator(MonitorDecorator):
            def _infer_context_type(self, instance: Any) -> str:
                return "WORKFLOW"

        return WorkflowMonitorDecorator(name=name)

    def _create_node_monitor(self, name: str):
        """Create a monitoring decorator that forces NODE type."""

        class NodeMonitorDecorator(MonitorDecorator):
            def _infer_context_type(self, instance: Any) -> str:
                return "NODE"

        return NodeMonitorDecorator(name=name)
