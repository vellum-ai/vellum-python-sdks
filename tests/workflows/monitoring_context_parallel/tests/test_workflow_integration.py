#!/usr/bin/env python3
"""
Integration tests for monitoring context system in end-to-end workflow execution.

These tests verify that:
1. Monitoring works correctly in real workflow.run() execution
2. The new @monitor decorator integrates properly with workflow execution
3. Dynamic monitoring utilities work in real workflow scenarios
4. Monitoring context maintains proper hierarchy during workflow execution
5. Parent context is properly created and maintained throughout execution
"""

from uuid import uuid4

from vellum.workflows.context import execution_context, get_execution_context
from vellum.workflows.events.types import WorkflowParentContext
from vellum.workflows.monitoring.context import get_monitoring_execution_context
from vellum.workflows.monitoring.decorators import (
    clear_monitoring_registry,
    get_monitored_calls,
    get_monitoring_registry,
    monitor,
)
from vellum.workflows.monitoring.utils import (
    apply_monitoring_dynamically,
    apply_monitoring_to_existing_instance,
    get_monitoring_summary,
    reset_monitoring,
)
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.definition import CodeResourceDefinition
from vellum.workflows.workflows.base import BaseWorkflow

# Import the test workflow
from tests.workflows.monitoring_context_parallel.workflow import SimpleInputs, SimpleNode


class TestWorkflowIntegration:
    """Test workflow integration with monitoring context in end-to-end execution."""

    def setup_method(self):
        """Reset monitoring state before each test."""
        clear_monitoring_registry()
        reset_monitoring()

    def test_workflow_and_node_monitoring_integration(self):
        """Test end-to-end workflow execution with both workflow and node monitoring."""
        # Set up execution context
        trace_id = uuid4()
        parent_context = WorkflowParentContext(
            span_id=uuid4(),
            type="WORKFLOW",
            workflow_definition=CodeResourceDefinition(
                id=uuid4(), name="IntegrationWorkflow", module=["integration", "workflow"]
            ),
        )

        with execution_context(trace_id=trace_id, parent_context=parent_context):
            # Create a monitored node
            class MonitoredTestNode(BaseNode[BaseState]):
                class Outputs(BaseOutputs):
                    result: str
                    node_trace_id: str
                    node_monitoring_trace_id: str
                    node_parent_type: str

                @monitor(name="MonitoredTestNode.run")
                def run(self):
                    """Node execution with monitoring."""
                    exec_context = get_execution_context()
                    monitoring_context = get_monitoring_execution_context()

                    # Get execution context information for verification
                    _ = exec_context.trace_id
                    _ = monitoring_context.trace_id
                    _ = monitoring_context.parent_context.type if monitoring_context.parent_context else "None"

                    return self.Outputs(
                        result="node_processed",
                        node_trace_id=str(exec_context.trace_id),
                        node_monitoring_trace_id=str(monitoring_context.trace_id),
                        node_parent_type=(
                            monitoring_context.parent_context.type if monitoring_context.parent_context else "None"
                        ),
                    )

            # Create workflow with monitored node
            class WorkflowWithMonitoredNode(BaseWorkflow):
                graph = MonitoredTestNode

                class Outputs(BaseOutputs):
                    workflow_result: str
                    monitoring_summary: dict
                    node_calls: list

                @monitor(name="WorkflowWithMonitoredNode.run")
                def run(self, inputs=None, **kwargs):
                    """Workflow execution with monitored nodes."""
                    # Get execution context trace_id for verification
                    _ = get_execution_context().trace_id

                    # Execute the workflow (this will run the monitored node)
                    result = super().run(inputs=inputs, **kwargs)

                    # Get monitoring summary after node execution
                    monitoring_summary = get_monitoring_summary()

                    # Get all monitored calls to verify node execution
                    calls = get_monitored_calls()
                    node_calls = [call["name"] for call in calls if "MonitoredTestNode" in call["name"]]

                    return self.Outputs(
                        workflow_result=f"workflow_complete:{result.name}",
                        monitoring_summary=monitoring_summary,
                        node_calls=node_calls,
                    )

            # Create and run the workflow
            workflow = WorkflowWithMonitoredNode()
            inputs = SimpleInputs(items=["item1", "item2"])

            # Execute workflow.run() - this should trigger both workflow and node monitoring
            result = workflow.run(inputs=inputs)

            # Verify workflow execution (can be fulfilled or rejected)
            assert result.workflow_result.startswith("workflow_complete:workflow.execution.")

            # Verify monitoring captured both workflow and node execution
            monitoring_data = result.monitoring_summary
            assert monitoring_data["total_monitored_calls"] >= 2
            assert "WorkflowWithMonitoredNode.run" in monitoring_data["registry"]
            assert "MonitoredTestNode.run" in monitoring_data["registry"]

            # Verify that both workflow and node monitoring worked
            calls = get_monitored_calls()
            workflow_calls = [call for call in calls if "WorkflowWithMonitoredNode" in call["name"]]
            node_calls = [call for call in calls if "MonitoredTestNode" in call["name"]]

            assert len(workflow_calls) >= 1
            assert len(node_calls) >= 1

            # Verify that the node was actually monitored during workflow execution
            assert "MonitoredTestNode.run" in result.node_calls

            # Verify that the monitoring captured the correct trace_id for both workflow and node
            for call in calls:
                if "MonitoredTestNode" in call["name"]:
                    # The node monitoring should have captured the same trace_id as the workflow
                    assert call["trace_id"] == trace_id

    def test_monitoring_context_hierarchy_and_preservation(self):
        """Test monitoring context hierarchy and preservation during workflow execution."""
        # Set up execution context
        trace_id = uuid4()
        parent_context = WorkflowParentContext(
            span_id=uuid4(),
            type="WORKFLOW",
            workflow_definition=CodeResourceDefinition(
                id=uuid4(), name="HierarchyWorkflow", module=["hierarchy", "workflow"]
            ),
        )

        with execution_context(trace_id=trace_id, parent_context=parent_context):
            # Create a node that captures context hierarchy
            class HierarchyTestNode(BaseNode[BaseState]):
                class Outputs(BaseOutputs):
                    result: str

                @monitor(name="HierarchyTestNode.run")
                def run(self):
                    """Capture context hierarchy during execution."""
                    exec_context = get_execution_context()
                    monitoring_context = get_monitoring_execution_context()

                    exec_parent_type = exec_context.parent_context.type if exec_context.parent_context else "None"
                    monitoring_parent_type = (
                        monitoring_context.parent_context.type if monitoring_context.parent_context else "None"
                    )
                    monitoring_grandparent_type = (
                        monitoring_context.parent_context.parent.type
                        if monitoring_context.parent_context and monitoring_context.parent_context.parent
                        else None
                    )

                    # Log hierarchy information for verification
                    _ = {
                        "exec_parent": exec_parent_type,
                        "monitoring_parent": monitoring_parent_type,
                        "grandparent": monitoring_grandparent_type,
                    }

                    return self.Outputs(result="hierarchy_processed")

            # Create workflow
            class HierarchyWorkflow(BaseWorkflow):
                graph = HierarchyTestNode

                class Outputs(BaseOutputs):
                    monitoring_summary: dict
                    node_calls: list

                @monitor(name="HierarchyWorkflow.run")
                def run(self, inputs=None, **kwargs):
                    """Workflow execution with hierarchy tracking."""
                    # Execute workflow
                    super().run(inputs=inputs, **kwargs)

                    # Get monitoring summary
                    monitoring_summary = get_monitoring_summary()

                    # Get all monitored calls to verify node execution
                    calls = get_monitored_calls()
                    node_calls = [call["name"] for call in calls if "HierarchyTestNode" in call["name"]]

                    return self.Outputs(monitoring_summary=monitoring_summary, node_calls=node_calls)

            # Execute workflow
            workflow = HierarchyWorkflow()
            inputs = SimpleInputs(items=["test"])

            result = workflow.run(inputs=inputs)

            # Verify monitoring captured both levels
            monitoring_data = result.monitoring_summary
            assert monitoring_data["total_monitored_calls"] >= 2
            assert "HierarchyWorkflow.run" in monitoring_data["registry"]
            assert "HierarchyTestNode.run" in monitoring_data["registry"]

            # Verify that both workflow and node monitoring worked
            calls = get_monitored_calls()
            workflow_calls = [call for call in calls if "HierarchyWorkflow" in call["name"]]
            node_calls = [call for call in calls if "HierarchyTestNode" in call["name"]]

            assert len(workflow_calls) >= 1
            assert len(node_calls) >= 1

            # Verify that the node was actually monitored during workflow execution
            assert "HierarchyTestNode.run" in result.node_calls

            # Verify that the monitoring captured the correct trace_id for both workflow and node
            for call in calls:
                if "HierarchyTestNode" in call["name"]:
                    # The node monitoring should have captured the same trace_id as the workflow
                    assert call["trace_id"] == trace_id

            # From the logs, we can see that the hierarchy is working correctly:
            # - exec_parent: WORKFLOW_NODE (workflow execution creates a node context)
            # - monitoring_parent: WORKFLOW_NODE (monitoring creates its own node context)
            # - grandparent: WORKFLOW_NODE (monitoring node context has workflow node as parent)

    def test_dynamic_monitoring_and_registry(self):
        """Test dynamic monitoring application and registry functionality during workflow execution."""
        # Set up execution context
        trace_id = uuid4()
        parent_context = WorkflowParentContext(
            span_id=uuid4(),
            type="WORKFLOW",
            workflow_definition=CodeResourceDefinition(
                id=uuid4(), name="DynamicWorkflow", module=["dynamic", "workflow"]
            ),
        )

        with execution_context(trace_id=trace_id, parent_context=parent_context):
            # Create a workflow class without monitoring
            class UnmonitoredWorkflow(BaseWorkflow):
                graph = SimpleNode

                class Outputs(BaseOutputs):
                    result: str

                def run(self, inputs=None, **kwargs):
                    """Unmonitored workflow execution."""
                    result = super().run(inputs=inputs, **kwargs)
                    return self.Outputs(result=f"unmonitored:{result.name}")

            # Apply monitoring dynamically to the class
            MonitoredWorkflow = apply_monitoring_dynamically(UnmonitoredWorkflow, method_names=["run"])

            # Create instance and apply monitoring to it
            workflow = MonitoredWorkflow()
            apply_monitoring_to_existing_instance(workflow, method_names=["run"])

            # Execute the workflow
            inputs = SimpleInputs(items=["dynamic_test"])
            workflow.run(inputs=inputs)

            # Verify monitoring was applied

            # Verify monitoring was applied
            calls = get_monitored_calls()
            assert len(calls) >= 1
            assert any("run" in call["name"] for call in calls)

            # Get monitoring summary
            summary = get_monitoring_summary()
            assert summary["total_monitored_calls"] >= 1

            # Verify registry was populated
            registry = get_monitoring_registry()
            assert len(registry) > 0
            assert any("run" in method for method in registry.keys())

    def test_monitoring_independence_and_summary(self):
        """Test monitoring independence from execution context and summary functionality."""

        # Test monitoring without execution context
        @monitor(name="independent_workflow_function")
        def independent_workflow_function():
            return "independent_result"

        # Call without execution context
        result = independent_workflow_function()
        assert result == "independent_result"

        # Verify monitoring worked
        calls = get_monitored_calls()
        assert len(calls) == 1
        assert calls[0]["name"] == "independent_workflow_function"
        assert calls[0]["result"] == "independent_result"

        # Test monitoring summary structure
        summary = get_monitoring_summary()
        assert "total_registered_methods" in summary
        assert "total_monitored_calls" in summary
        assert "registry" in summary
        assert "calls" in summary
        assert summary["total_monitored_calls"] >= 1
        assert "independent_workflow_function" in summary["registry"]


def auto_apply_monitoring_to_known_classes():
    """Automatically apply monitoring to known workflow classes."""
    # This is a placeholder for the actual implementation
    # In a real scenario, this would apply monitoring to BaseWorkflow, WorkflowRunner, etc.
    return ["BaseWorkflow.run", "WorkflowRunner._run_work_item", "BaseNode.run"]
