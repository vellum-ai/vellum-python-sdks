from vellum.workflows.triggers import ScheduleTrigger


class Scheduled(ScheduleTrigger):
    class Config:
        cron = "* * * * *"
        timezone = "America/New_York"

    class Display(ScheduleTrigger.Display):
        label = "Scheduled"
        x = 442.51836734693876
        y = -200.23394451530612
        z_index = 4
        icon = "vellum:icon:clock"
