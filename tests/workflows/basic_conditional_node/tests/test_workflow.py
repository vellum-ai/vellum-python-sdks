from vellum.workflows.constants import undefined

from tests.workflows.basic_conditional_node.workflow import CategoryWorkflow, Inputs
from tests.workflows.basic_conditional_node.workflow_with_try_node import Inputs as TryInputs, Workflow


def test_run_workflow__question():
    workflow = CategoryWorkflow()

    terminal_event = workflow.run(inputs=Inputs(category="question"))

    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event
    assert terminal_event.outputs.question == "question"
    assert terminal_event.outputs.complaint is undefined
    assert terminal_event.outputs.compliment is undefined
    assert terminal_event.outputs.statement is undefined
    assert terminal_event.outputs.fallthrough is undefined


def test_run_workflow__complaint():
    workflow = CategoryWorkflow()

    terminal_event = workflow.run(inputs=Inputs(category="complaint"))

    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event
    assert terminal_event.outputs.question is undefined
    assert terminal_event.outputs.complaint == "complaint"
    assert terminal_event.outputs.compliment is undefined
    assert terminal_event.outputs.statement is undefined
    assert terminal_event.outputs.fallthrough is undefined


def test_run_workflow__compliment():
    workflow = CategoryWorkflow()

    terminal_event = workflow.run(inputs=Inputs(category="compliment"))

    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event
    assert terminal_event.outputs.question is undefined
    assert terminal_event.outputs.complaint is undefined
    assert terminal_event.outputs.compliment == "compliment"
    assert terminal_event.outputs.statement is undefined
    assert terminal_event.outputs.fallthrough is undefined


def test_run_workflow__statement():
    workflow = CategoryWorkflow()

    terminal_event = workflow.run(inputs=Inputs(category="statement"))

    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event
    assert terminal_event.outputs.question is undefined
    assert terminal_event.outputs.complaint is undefined
    assert terminal_event.outputs.compliment is undefined
    assert terminal_event.outputs.statement == "statement"
    assert terminal_event.outputs.fallthrough is undefined


def test_run_workflow__fallthrough():
    workflow = CategoryWorkflow()

    terminal_event = workflow.run(inputs=Inputs(category="lol"))

    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event
    assert terminal_event.outputs.question is undefined
    assert terminal_event.outputs.complaint is undefined
    assert terminal_event.outputs.compliment is undefined
    assert terminal_event.outputs.statement is undefined
    assert terminal_event.outputs.fallthrough == "lol"


def test_run_workflow__try_none():
    workflow = Workflow()
    terminal_event = workflow.run(inputs=TryInputs(name="mar"))
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert terminal_event.outputs.pass_final_output == "pass"
    assert terminal_event.outputs.fail_final_output is undefined
