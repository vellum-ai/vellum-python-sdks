from datetime import datetime
from typing import Optional

from vellum.workflows.triggers.base import BaseTrigger


class ScheduleTrigger(BaseTrigger):
    """
    Trigger representing time-based workflow invocation.
    Supports Cron-based schedules (e.g., "0 9 * * MON" for every Monday at 9am)
    """

    name: Optional[str] = "Scheduled"

    current_run_at: datetime
    next_run_at: datetime

    class Config:
        cron: str
        timezone: Optional[str] = None
