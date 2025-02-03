from vellum.client.core.pydantic_utilities import UniversalBaseModel


def test_load_workflow_event_display_context():
    from vellum_ee.workflows.display.types import WorkflowEventDisplayContext

    # We are actually just ensuring there are no circular dependencies when
    # our Workflow Server imports this class.
    assert issubclass(WorkflowEventDisplayContext, UniversalBaseModel)
