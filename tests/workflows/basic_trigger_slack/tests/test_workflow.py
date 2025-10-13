from vellum.workflows.edges.trigger_edge import TriggerEdge
from vellum.workflows.triggers.slack import SlackTrigger

from tests.workflows.basic_trigger_slack.workflow import ProcessMessageNode, SlackTriggerWorkflow


def test_slack_trigger_workflow__has_trigger():
    # GIVEN a workflow with SlackTrigger
    subgraphs = SlackTriggerWorkflow.get_subgraphs()

    # THEN it should have trigger edges
    trigger_edges = next((subgraph.trigger_edges) for subgraph in subgraphs if subgraph.trigger_edges)

    # THEN it should have the correct trigger edge
    assert list(trigger_edges) == [TriggerEdge(SlackTrigger, ProcessMessageNode)]
