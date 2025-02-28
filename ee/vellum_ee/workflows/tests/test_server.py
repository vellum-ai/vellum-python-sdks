from vellum.client.core.pydantic_utilities import UniversalBaseModel


def test_load_workflow_event_display_context():
    # DEPRECATED: Use `vellum.workflows.events.workflow.WorkflowEventDisplayContext` instead. Will be removed in 0.15.0
    from vellum_ee.workflows.display.types import WorkflowEventDisplayContext

    # We are actually just ensuring there are no circular dependencies when
    # our Workflow Server imports this class.
    assert issubclass(WorkflowEventDisplayContext, UniversalBaseModel)
