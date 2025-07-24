import logging
import threading
from unittest.mock import patch
from uuid import uuid4
from typing import Any, Dict, List

from vellum.workflows.context import execution_context
from vellum.workflows.events.context import (
    _monitoring_context_store,
    set_monitoring_execution_context as set_monitoring_execution_context_ctx,
)
from vellum.workflows.events.decorators import set_monitoring_execution_context as set_monitoring_execution_context_deco

from .workflow import Inputs, SimpleMapExample

logger = logging.getLogger(__name__)


def test_mapnode_monitoring_context_flow():
    """Test that monitoring creates the correct workflow→node→workflow→node parent context hierarchy."""

    # Capture all parent contexts created during execution
    captured_contexts: List[Dict[str, Any]] = []

    # Store original functions to avoid circular calls
    original_context_setter = set_monitoring_execution_context_ctx
    original_decorator_setter = set_monitoring_execution_context_deco

    def capture_monitoring_context(context):
        """Capture parent context hierarchy when monitoring contexts are set."""
        if context.parent_context:
            # Build complete parent context chain
            parent_chain: List[Dict[str, Any]] = []
            current_parent = context.parent_context

            while current_parent is not None:
                workflow_def = getattr(current_parent, "workflow_definition", None)
                node_def = getattr(current_parent, "node_definition", None)
                definition = workflow_def or node_def

                name = getattr(definition, "name", "unknown") if definition else "unknown"

                parent_info = {
                    "type": current_parent.type,
                    "name": name,
                }
                parent_chain.append(parent_info)
                current_parent = getattr(current_parent, "parent", None)

                if len(parent_chain) > 10:  # Safety limit
                    break

            captured_contexts.append(
                {"trace_id": str(context.trace_id)[:8], "parent_chain": parent_chain, "chain_length": len(parent_chain)}
            )

        # Call the original function to maintain monitoring functionality
        return original_context_setter(context)

    def capture_monitoring_context_decorator(context):
        """Capture parent context hierarchy when monitoring contexts are set (decorator version)."""
        if context.parent_context:
            # Build complete parent context chain
            parent_chain: List[Dict[str, Any]] = []
            current_parent = context.parent_context

            while current_parent is not None:
                workflow_def = getattr(current_parent, "workflow_definition", None)
                node_def = getattr(current_parent, "node_definition", None)
                definition = workflow_def or node_def

                name = getattr(definition, "name", "unknown") if definition else "unknown"

                parent_info = {
                    "type": current_parent.type,
                    "name": name,
                }
                parent_chain.append(parent_info)
                current_parent = getattr(current_parent, "parent", None)

                if len(parent_chain) > 10:  # Safety limit
                    break

            captured_contexts.append(
                {"trace_id": str(context.trace_id)[:8], "parent_chain": parent_chain, "chain_length": len(parent_chain)}
            )

        # Call the original function to maintain monitoring functionality
        return original_decorator_setter(context)

    with patch(
        "vellum.workflows.events.context.set_monitoring_execution_context", side_effect=capture_monitoring_context
    ), patch(
        "vellum.workflows.events.decorators.set_monitoring_execution_context",
        side_effect=capture_monitoring_context_decorator,
    ):
        # Run workflow to capture parent context hierarchy
        workflow = SimpleMapExample()
        inputs = Inputs(fruits=["apple", "banana"])

        with execution_context(trace_id=uuid4()):
            result = workflow.run(inputs=inputs)

        # Verify workflow succeeded
        assert result.name == "workflow.execution.fulfilled"
        if hasattr(result, "outputs"):
            assert result.outputs == {"final_value": [5, 7]}  # len("apple")+0, len("banana")+1

        # Verify we captured monitoring contexts
        assert len(captured_contexts) > 0, "No monitoring contexts captured. Expected contexts for workflow execution."

        # Debug: Log all captured contexts to understand the actual pattern
        logger.info(f"Captured {len(captured_contexts)} monitoring contexts:")
        for i, ctx in enumerate(captured_contexts):
            logger.info(f"  Context {i}: depth={ctx['chain_length']}, trace={ctx['trace_id']}")
            for j, parent in enumerate(ctx["parent_chain"]):
                logger.info(f"    Level {j}: {parent['name']} ({parent['type']})")

        # Find the deepest context (should be from deepest execution level)
        deepest_context = max(captured_contexts, key=lambda x: int(x["chain_length"]))

        # Verify we have reasonable depth
        assert (
            deepest_context["chain_length"] >= 3
        ), f"Expected at least 3 levels in parent chain, got {deepest_context['chain_length']}"

        # Verify the parent context hierarchy follows the expected execution pattern
        # Now with proper WORKFLOW/WORKFLOW_NODE distinction
        actual_chain = deepest_context["parent_chain"]

        # Check that we have mixed types now (not all WORKFLOW)
        actual_types = [ctx["type"] for ctx in actual_chain]
        unique_types = set(actual_types)

        # Should have both WORKFLOW and WORKFLOW_NODE types
        expected_types = {"WORKFLOW", "WORKFLOW_NODE"}
        assert (
            len(unique_types.intersection(expected_types)) > 1
        ), f"Expected mix of WORKFLOW and WORKFLOW_NODE types, got only: {unique_types}"

        # Verify core execution components are present
        chain_names = [ctx["name"] for ctx in actual_chain]

        # The dynamic system successfully captures the core execution flow
        # Main components we should see: SimpleMapExample.run, MapFruitsNode.run, internal MapNode methods
        core_components = ["SimpleMapExample.run", "MapFruitsNode.run"]

        # Verify we have the main workflow and node components
        present_core = [comp for comp in core_components if comp in chain_names]
        assert (
            len(present_core) >= 2
        ), f"Expected core components {core_components}, found {present_core} in {chain_names}"

        # Verify root is main workflow
        root_context = actual_chain[-1]
        assert (
            root_context["name"] == "SimpleMapExample.run"
        ), f"Expected SimpleMapExample.run as root, got '{root_context['name']}'"
        assert root_context["type"] == "WORKFLOW", f"Expected root to be WORKFLOW type, got '{root_context['type']}'"

        logger.info("Successfully verified dynamic monitoring with proper type classification:")
        logger.info(f"  Deepest chain has {deepest_context['chain_length']} levels")
        logger.info(f"  Type variety: {unique_types}")
        logger.info(f"  Core components found: {present_core}")
        logger.info(f"  Root: {root_context['name']} ({root_context['type']})")


def test_monitoring_context_storage_and_retrieval():
    """Test that monitoring context is properly stored and retrieved across thread boundaries."""

    # Track context store operations
    operations: List[Dict[str, Any]] = []

    original_store = _monitoring_context_store.store_context
    original_retrieve = _monitoring_context_store.retrieve_context

    def track_store(trace_id, parent_context):
        if parent_context:
            operations.append(
                {
                    "action": "store",
                    "context_type": getattr(parent_context, "type", None),
                    "thread_id": threading.get_ident(),
                }
            )
        return original_store(trace_id, parent_context)

    def track_retrieve(trace_id, current_parent_context=None):
        result = original_retrieve(trace_id, current_parent_context)
        operations.append({"action": "retrieve", "found": result is not None, "thread_id": threading.get_ident()})
        return result

    with patch.object(_monitoring_context_store, "store_context", side_effect=track_store), patch.object(
        _monitoring_context_store, "retrieve_context", side_effect=track_retrieve
    ):
        # Run workflow with concurrent MapNode execution
        workflow = SimpleMapExample()
        inputs = Inputs(fruits=["a", "bb", "ccc"])  # Different lengths for verification

        with execution_context(trace_id=uuid4()):
            result = workflow.run(inputs=inputs)

        # Verify workflow succeeded with expected outputs
        if hasattr(result, "outputs"):
            assert result.outputs == {"final_value": [1, 3, 5]}  # [1+0, 2+1, 3+2]

        # Analyze context operations
        stores = [op for op in operations if op["action"] == "store"]
        retrievals = [op for op in operations if op["action"] == "retrieve"]
        successful_retrievals = [op for op in retrievals if op["found"]]

        # Verify we have reasonable context activity
        assert len(stores) > 10, f"Expected significant context storage activity, got {len(stores)}"
        assert len(retrievals) > 5, f"Expected context retrieval activity, got {len(retrievals)}"

        # Verify high success rate for retrievals (some initial calls may fail as expected)
        success_rate = len(successful_retrievals) / len(retrievals) if retrievals else 0
        assert success_rate > 0.5, f"Context retrieval success rate too low: {success_rate:.2%}"

        # Verify context types are being stored (may all be WORKFLOW or mixed)
        context_types = {op["context_type"] for op in stores}
        assert len(context_types) > 0, "No context types were stored"

        # Log context activity for debugging
        logger.info(
            f"Context operations: {len(stores)} stores,"
            f" {len(successful_retrievals)}/{len(retrievals)} successful retrievals"
        )
        logger.info(f"Context types observed: {context_types}")
