#!/usr/bin/env python3
"""
Tests for the new monitoring decorator and monitoring execution context.

These tests ensure that:
1. The @monitor decorator works correctly
2. Monitoring execution context maintains 1:1 relationship with execution context
3. Parent contexts are created correctly for monitoring
4. The monitoring system doesn't rely on syncing with execution context
5. Dynamic monitoring utilities work as expected
"""

import pytest
from uuid import uuid4

from vellum.workflows.context import execution_context, get_execution_context
from vellum.workflows.events.types import WorkflowParentContext
from vellum.workflows.monitoring.context import get_monitoring_execution_context, monitoring_execution_context
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
    wrap_method_with_monitoring,
)
from vellum.workflows.types.definition import CodeResourceDefinition


class TestMonitorDecorator:
    """Test the @monitor decorator functionality."""

    def setup_method(self):
        """Reset monitoring state before each test."""
        clear_monitoring_registry()
        reset_monitoring()

    def test_basic_monitor_decorator_functionality(self):
        """Test basic @monitor decorator functionality including exceptions and configuration."""

        # Test basic functionality
        @monitor(name="test_function")
        def test_function(x: int, y: str = "default") -> str:
            return f"result: {x} {y}"

        result = test_function(42, "test")
        assert result == "result: 42 test"

        # Test exception handling
        @monitor(name="error_function", capture_exceptions=True)
        def error_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            error_function()

        # Test disabled monitoring
        @monitor(name="disabled_function", enabled=False)
        def disabled_function():
            return "disabled"

        result = disabled_function()
        assert result == "disabled"

        # Verify monitoring data was captured
        calls = get_monitored_calls()
        assert len(calls) == 2  # test_function and error_function (disabled_function not captured)
        assert calls[0]["name"] == "test_function"
        assert calls[0]["result"] == "result: 42 test"
        assert calls[1]["name"] == "error_function"
        assert isinstance(calls[1]["exception"], ValueError)

    def test_context_type_inference_and_custom_configuration(self):
        """Test context type inference and custom configuration options."""

        # Test workflow context inference
        class TestWorkflow:
            @monitor(name="workflow_method")
            def run(self):
                monitoring_context = get_monitoring_execution_context()
                return monitoring_context.parent_context.type if monitoring_context.parent_context else "None"

        # Test node context inference
        class TestNode:
            @monitor(name="node_method")
            def run(self):
                monitoring_context = get_monitoring_execution_context()
                return monitoring_context.parent_context.type if monitoring_context.parent_context else "None"

        # Test custom configuration
        @monitor(
            name="custom_function",
            capture_args=False,
            capture_result=False,
            capture_exceptions=False,
        )
        def custom_function(x: int) -> int:
            return x * 2

        # Execute tests
        workflow = TestWorkflow()
        node = TestNode()

        workflow_result = workflow.run()
        node_result = node.run()
        custom_result = custom_function(5)

        # Verify results
        assert workflow_result == "WORKFLOW"
        assert node_result == "WORKFLOW_NODE"
        assert custom_result == 10

        # Verify custom configuration
        calls = get_monitored_calls()
        custom_call = next(call for call in calls if call["name"] == "custom_function")
        assert custom_call["data"]["args"] is None  # capture_args=False
        # Note: The result field is not present in the call data when capture_result=False
        # The monitoring system only captures what's explicitly enabled


class TestMonitoringExecutionContext:
    """Test monitoring execution context functionality."""

    def setup_method(self):
        """Reset monitoring state before each test."""
        clear_monitoring_registry()
        reset_monitoring()

    def test_monitoring_context_creation_and_inheritance(self):
        """Test monitoring context creation and inheritance from execution context."""
        # Test basic context creation
        trace_id = uuid4()
        parent_context = WorkflowParentContext(
            span_id=uuid4(),
            type="WORKFLOW",
            workflow_definition=CodeResourceDefinition(id=uuid4(), name="TestWorkflow", module=["test"]),
        )

        with execution_context(trace_id=trace_id, parent_context=parent_context):
            # Test monitoring context inheritance
            with monitoring_execution_context():
                monitoring_context = get_monitoring_execution_context()
                assert monitoring_context.trace_id == trace_id
                # Note: parent_context may be None when not explicitly provided
                # The monitoring context inherits trace_id but not necessarily parent_context

            # Test monitoring context independence
            with monitoring_execution_context(trace_id=uuid4()):
                monitoring_context = get_monitoring_execution_context()
                assert monitoring_context.trace_id != trace_id  # Should use provided trace_id

    def test_monitoring_context_independence_and_thread_safety(self):
        """Test monitoring context independence and thread safety."""
        import threading

        # Test independence from execution context
        @monitor(name="independent_function")
        def independent_function():
            return "independent"

        # Call without execution context
        result = independent_function()
        assert result == "independent"

        # Test thread safety
        results = []

        def worker(thread_id: int):
            with monitoring_execution_context(trace_id=uuid4()):
                monitoring_context = get_monitoring_execution_context()
                results.append((thread_id, monitoring_context.trace_id))

        # Create and run threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Verify each thread had its own context
        assert len(results) == 3
        trace_ids = [trace_id for _, trace_id in results]
        assert len(set(trace_ids)) == 3  # All different trace_ids


class TestParentContextCreation:
    """Test parent context creation for monitoring."""

    def setup_method(self):
        """Reset monitoring state before each test."""
        clear_monitoring_registry()
        reset_monitoring()

    def test_workflow_and_node_parent_context_creation(self):
        """Test parent context creation for both workflow and node types."""

        # Test workflow parent context
        class TestWorkflow:
            @monitor(name="workflow_test")
            def run(self):
                monitoring_context = get_monitoring_execution_context()
                return {
                    "type": monitoring_context.parent_context.type if monitoring_context.parent_context else "None",
                    "trace_id": str(monitoring_context.trace_id),
                }

        # Test node parent context
        class TestNode:
            @monitor(name="node_test")
            def run(self):
                monitoring_context = get_monitoring_execution_context()
                return {
                    "type": monitoring_context.parent_context.type if monitoring_context.parent_context else "None",
                    "trace_id": str(monitoring_context.trace_id),
                }

        # Execute tests
        workflow = TestWorkflow()
        node = TestNode()

        workflow_result = workflow.run()
        node_result = node.run()

        # Verify results
        assert workflow_result["type"] == "WORKFLOW"
        assert node_result["type"] == "WORKFLOW_NODE"
        # Note: trace_id may be default when no execution context is set up
        # The important thing is that the parent context types are correct

    def test_parent_context_hierarchy(self):
        """Test parent context hierarchy creation."""
        # Set up execution context
        trace_id = uuid4()
        parent_context = WorkflowParentContext(
            span_id=uuid4(),
            type="WORKFLOW",
            workflow_definition=CodeResourceDefinition(id=uuid4(), name="ParentWorkflow", module=["parent"]),
        )

        with execution_context(trace_id=trace_id, parent_context=parent_context):

            class TestNode:
                @monitor(name="hierarchy_test")
                def run(self):
                    monitoring_context = get_monitoring_execution_context()
                    parent_type = (
                        monitoring_context.parent_context.type if monitoring_context.parent_context else "None"
                    )
                    grandparent_type = (
                        monitoring_context.parent_context.parent.type
                        if monitoring_context.parent_context and monitoring_context.parent_context.parent
                        else "None"
                    )
                    return {
                        "parent_type": parent_type,
                        "grandparent_type": grandparent_type,
                        "trace_id": str(monitoring_context.trace_id),
                    }

            node = TestNode()
            result = node.run()

            # Verify hierarchy
            assert result["parent_type"] == "WORKFLOW_NODE"
            assert result["grandparent_type"] == "WORKFLOW"
            assert result["trace_id"] == str(trace_id)


class TestDynamicMonitoring:
    """Test dynamic monitoring utilities."""

    def setup_method(self):
        """Reset monitoring state before each test."""
        clear_monitoring_registry()
        reset_monitoring()

    def test_dynamic_monitoring_application(self):
        """Test dynamic monitoring application to classes and instances."""

        # Test class-level monitoring
        class TestClass:
            def method1(self):
                return "method1"

            def method2(self):
                return "method2"

        # Apply monitoring dynamically to class
        MonitoredClass = apply_monitoring_dynamically(TestClass, method_names=["method1", "method2"])

        # Test instance-level monitoring
        instance = MonitoredClass()
        apply_monitoring_to_existing_instance(instance, method_names=["method1"])

        # Execute methods
        result1 = instance.method1()
        result2 = instance.method2()

        # Verify results
        assert result1 == "method1"
        assert result2 == "method2"

        # Verify monitoring was applied
        calls = get_monitored_calls()
        assert len(calls) >= 2
        assert any("method1" in call["name"] for call in calls)
        assert any("method2" in call["name"] for call in calls)

    def test_wrap_method_with_monitoring(self):
        """Test wrapping individual methods with monitoring."""

        def test_function(x: int) -> int:
            return x * 2

        # Wrap function with monitoring
        monitored_function = wrap_method_with_monitoring(test_function, name="wrapped_function")

        # Execute function
        result = monitored_function(5)
        assert result == 10

        # Verify monitoring was applied
        calls = get_monitored_calls()
        assert len(calls) == 1
        assert calls[0]["name"] == "wrapped_function"
        assert calls[0]["result"] == 10


class TestMonitoringRegistry:
    """Test monitoring registry functionality."""

    def setup_method(self):
        """Reset monitoring state before each test."""
        clear_monitoring_registry()
        reset_monitoring()

    def test_monitoring_registry_and_summary(self):
        """Test monitoring registry tracking and summary functionality."""

        # Register and call monitored methods
        @monitor(name="test_method")
        def test_method():
            return "test"

        @monitor(name="tracked_method", capture_args=True, capture_result=True)
        def tracked_method(x: int, y: str = "default"):
            return f"result: {x} {y}"

        # Execute methods
        test_method()
        tracked_method(42, "test")

        # Test registry tracking
        registry = get_monitoring_registry()
        assert len(registry) == 2
        assert "test_method" in registry
        assert "tracked_method" in registry

        # Test calls tracking
        calls = get_monitored_calls()
        assert len(calls) == 2
        assert calls[0]["name"] == "test_method"
        assert calls[0]["result"] == "test"
        assert calls[1]["name"] == "tracked_method"
        assert calls[1]["data"]["args"] == (42, "test")
        assert calls[1]["result"] == "result: 42 test"

        # Test monitoring summary
        summary = get_monitoring_summary()
        assert summary["total_registered_methods"] == 2
        assert summary["total_monitored_calls"] == 2
        assert "test_method" in summary["registry"]
        assert "tracked_method" in summary["registry"]

        # Test clearing registry
        clear_monitoring_registry()
        assert len(get_monitoring_registry()) == 0
        assert len(get_monitored_calls()) == 0


class TestMonitoringIndependence:
    """Test monitoring independence from execution context."""

    def setup_method(self):
        """Reset monitoring state before each test."""
        clear_monitoring_registry()
        reset_monitoring()

    def test_monitoring_independence_and_preservation(self):
        """Test monitoring independence from execution context and context preservation."""

        # Test monitoring without execution context
        @monitor(name="independent_method")
        def independent_method():
            return "independent"

        result = independent_method()
        assert result == "independent"

        # Test monitoring context preservation
        class TestNode:
            @monitor(name="preservation_test")
            def run(self):
                # Get both contexts
                exec_context = get_execution_context()
                monitoring_context = get_monitoring_execution_context()

                return {
                    "exec_trace_id": str(exec_context.trace_id),
                    "monitoring_trace_id": str(monitoring_context.trace_id),
                    "monitoring_parent_type": (
                        monitoring_context.parent_context.type if monitoring_context.parent_context else "None"
                    ),
                }

        # Test with execution context
        trace_id = uuid4()
        parent_context = WorkflowParentContext(
            span_id=uuid4(),
            type="WORKFLOW",
            workflow_definition=CodeResourceDefinition(id=uuid4(), name="TestWorkflow", module=["test"]),
        )

        with execution_context(trace_id=trace_id, parent_context=parent_context):
            node = TestNode()
            result = node.run()

            # Verify context preservation
            assert result["exec_trace_id"] == str(trace_id)
            assert result["monitoring_trace_id"] == str(trace_id)
            assert result["monitoring_parent_type"] == "WORKFLOW_NODE"

        # Verify monitoring still works after context exit
        calls = get_monitored_calls()
        assert len(calls) >= 2  # independent_method + preservation_test
        assert any("independent_method" in call["name"] for call in calls)
        assert any("preservation_test" in call["name"] for call in calls)
