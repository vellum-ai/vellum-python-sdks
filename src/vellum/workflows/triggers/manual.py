from vellum.workflows.triggers.base import BaseTrigger


class ManualTrigger(BaseTrigger):
    """
    Default trigger representing explicit workflow invocation.

    ManualTrigger is used when workflows are explicitly invoked via:
    - workflow.run() method calls
    - workflow.stream() method calls
    - API calls to execute the workflow

    This is the default trigger for all workflows. When no trigger is specified
    in a workflow's graph definition, ManualTrigger is implicitly added.

    Examples:
        # Explicit ManualTrigger (equivalent to implicit)
        class MyWorkflow(BaseWorkflow):
            graph = ManualTrigger >> MyNode

        # Implicit ManualTrigger (normalized to above)
        class MyWorkflow(BaseWorkflow):
            graph = MyNode

    Characteristics:
        - Provides no trigger-specific inputs
        - Always ready to execute when invoked
        - Simplest trigger type with no configuration
        - Default behavior for backward compatibility

    Comparison with other triggers:
        - IntegrationTrigger: Responds to external events (webhooks, API calls)
        - ScheduledTrigger: Executes based on time/schedule configuration
        - ManualTrigger: Executes when explicitly called
    """

    pass
