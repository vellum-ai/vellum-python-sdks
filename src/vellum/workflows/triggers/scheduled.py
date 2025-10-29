from vellum.workflows.triggers.base import BaseTrigger


class ScheduledTrigger(BaseTrigger):
    """
    Trigger representing time-based workflow invocation.

    ScheduledTrigger is used when workflows are invoked based on a schedule:
    - Cron-based schedules (e.g., "0 9 * * MON" for every Monday at 9am)
    - Interval-based schedules (e.g., every 5 minutes, hourly, daily)
    - One-time scheduled executions

    This trigger enables workflows to run automatically at specified times without
    manual invocation or external events.

    Examples:
        class DailyReportWorkflow(BaseWorkflow):
            graph = ScheduledTrigger >> GenerateReportNode

        class ScheduledMaintenanceWorkflow(BaseWorkflow):
            graph = ScheduledTrigger >> {CleanupNode, BackupNode}

    Characteristics:
        - Provides no trigger-specific inputs (schedule is configured externally)
        - Executes automatically based on time/schedule configuration
        - No runtime parameters needed
        - Schedule configuration managed by deployment settings

    Comparison with other triggers:
        - ManualTrigger: Executes when explicitly called
        - IntegrationTrigger: Responds to external events (webhooks, API calls)
        - ScheduledTrigger: Executes based on time/schedule configuration

    Note:
        The actual schedule (cron expression, interval, etc.) is configured at the
        deployment level, not in the trigger class itself. This trigger simply marks
        that the workflow should be invoked on a schedule.
    """

    pass
