from vellum.workflows.state.context import WorkflowContext


def process_with_context(ctx: WorkflowContext, query: str) -> str:
    """
    Process a query with access to the workflow context.
    The WorkflowContext parameter should be excluded from the function schema
    and automatically injected at runtime.
    """
    return f"Processed: {query}"
