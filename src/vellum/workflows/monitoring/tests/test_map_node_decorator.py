import logging
import threading
from uuid import uuid4

from vellum.workflows.context import execution_context

from ..context import _monitoring_context_store, set_monitoring_execution_context
from .workflow import Inputs, SimpleMapExample

logger = logging.getLogger(__name__)


def test_mapnode_monitoring_context_flow():
    """Test that monitoring creates the correct workflow→node→workflow→node parent context hierarchy."""

    # Capture all parent contexts created during execution
    captured_contexts = []

    original_set_context = set_monitoring_execution_context

    def capture_monitoring_context(context):
        """Capture parent context hierarchy when monitoring contexts are set."""
        if context.parent_context:
            # Build complete parent context chain
            parent_chain = []
            current_parent = context.parent_context

            while current_parent is not None:
                parent_info = {
                    "type": current_parent.type,
                    "name": getattr(
                        getattr(current_parent, "workflow_definition", None)
                        or getattr(current_parent, "node_definition", None),
                        "name",
                        "unknown",
                    ),
                }
                parent_chain.append(parent_info)
                current_parent = getattr(current_parent, "parent", None)

                if len(parent_chain) > 10:  # Safety limit
                    break

            captured_contexts.append(
                {"trace_id": str(context.trace_id)[:8], "parent_chain": parent_chain, "chain_length": len(parent_chain)}
            )

        return original_set_context(context)

    # Patch the context setter to capture hierarchy
    import vellum.workflows.monitoring.context

    vellum.workflows.monitoring.context.set_monitoring_execution_context = capture_monitoring_context

    try:
        # Run workflow to capture parent context hierarchy
        workflow = SimpleMapExample()
        inputs = Inputs(fruits=["apple", "banana"])

        with execution_context(trace_id=uuid4()):
            result = workflow.run(inputs=inputs)

        # Verify workflow succeeded
        assert result.name == "workflow.execution.fulfilled"
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
        deepest_context = max(captured_contexts, key=lambda x: x["chain_length"])

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
        internal_components = ["MapFruitsNode._run_subworkflow", "MapFruitsNode._context_run_subworkflow"]

        # Verify we have the main workflow and node components
        present_core = [comp for comp in core_components if comp in chain_names]
        assert (
            len(present_core) >= 2
        ), f"Expected core components {core_components}, found {present_core} in {chain_names}"

        # Verify we captured internal MapNode execution methods
        present_internal = [comp for comp in internal_components if comp in chain_names]
        assert (
            len(present_internal) >= 1
        ), f"Expected internal MapNode methods {internal_components}, found {present_internal} in {chain_names}"

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
        logger.info(f"  Internal methods captured: {present_internal}")
        logger.info(f"  Root: {root_context['name']} ({root_context['type']})")

    finally:
        # Restore original context setter
        vellum.workflows.monitoring.context.set_monitoring_execution_context = original_set_context


def test_monitoring_context_storage_and_retrieval():
    """Test that monitoring context is properly stored and retrieved across thread boundaries."""

    # Track context store operations
    operations = []

    original_store = _monitoring_context_store.store_context
    original_retrieve = _monitoring_context_store.retrieve_context

    def track_store(trace_id, parent_context):
        if parent_context:
            operations.append(
                {"action": "store", "context_type": parent_context.type, "thread_id": threading.get_ident()}
            )
        return original_store(trace_id, parent_context)

    def track_retrieve(trace_id, current_parent_context=None):
        result = original_retrieve(trace_id, current_parent_context)
        operations.append({"action": "retrieve", "found": result is not None, "thread_id": threading.get_ident()})
        return result

    _monitoring_context_store.store_context = track_store
    _monitoring_context_store.retrieve_context = track_retrieve

    try:
        # Run workflow with concurrent MapNode execution
        workflow = SimpleMapExample()
        inputs = Inputs(fruits=["a", "bb", "ccc"])  # Different lengths for verification

        with execution_context(trace_id=uuid4()):
            result = workflow.run(inputs=inputs)

        # Verify workflow succeeded with expected outputs
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

    finally:
        _monitoring_context_store.store_context = original_store
        _monitoring_context_store.retrieve_context = original_retrieve
