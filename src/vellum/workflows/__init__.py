import os
from uuid import uuid4
from typing import Optional

from .context import ExecutionContext
from .state.context import WorkflowContext
from .workflows.base import BaseWorkflow


def enable_workflow_monitoring(api_key: Optional[str] = None, api_url: Optional[str] = None) -> WorkflowContext:
    """
    Create a WorkflowContext with monitoring enabled.

    This is a convenience function for users who want to easily enable workflow
    monitoring without manually setting up VellumEmitter and context.

    Args:
        api_key: Vellum API key. If not provided, uses VELLUM_API_KEY environment variable.
        api_url: Vellum API URL. If not provided, uses VELLUM_API_URL environment variable or default.

    Returns:
        WorkflowContext configured for monitoring.

    Example:
        ```python
        from vellum.workflows import enable_workflow_monitoring

        # Enable monitoring with environment variables
        context = enable_workflow_monitoring()
        workflow = MyWorkflow(context=context)
        result = workflow.run()
        # Monitoring URL will be automatically printed

        # Or with explicit API key
        context = enable_workflow_monitoring(api_key="your-api-key")
        workflow = MyWorkflow(context=context)
        result = workflow.run()
        ```
    """
    from .vellum_client import create_vellum_client

    # Use provided API key or fall back to environment variable
    if api_key is None:
        api_key = os.getenv("VELLUM_API_KEY")

    if not api_key:
        raise ValueError(
            "API key is required for monitoring. Provide it via the api_key parameter "
            "or set the VELLUM_API_KEY environment variable."
        )

    vellum_client = create_vellum_client(api_key=api_key, api_url=api_url)

    # Create execution context with proper trace_id
    execution_context = ExecutionContext(trace_id=uuid4())

    return WorkflowContext(
        vellum_client=vellum_client,
        execution_context=execution_context,
        enable_monitoring=True,
    )


__all__ = [
    "BaseWorkflow",
    "enable_workflow_monitoring",
]
