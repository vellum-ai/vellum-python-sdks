from vellum.workflows.triggers import ManualTrigger


class Manual(ManualTrigger):
    class Display(ManualTrigger.Display):
        label = "Manual"
        x = 0
        y = 0
        z_index = 0
