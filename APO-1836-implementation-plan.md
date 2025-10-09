# Implementation Plan for APO-1836: Support workflow.run() and workflow.stream() for Integration Triggers

## Overview
Enable runtime execution of workflows with IntegrationTrigger (like SlackTrigger) by accepting trigger event data and making trigger outputs available to downstream nodes.

## Phase 1: Core Runtime Support

### 1. Extend BaseWorkflow.run() and BaseWorkflow.stream()
**File:** `src/vellum/workflows/workflows/base.py`

- Add `trigger_event: Optional[dict] = None` parameter to both methods
- Pass trigger_event to WorkflowRunner

### 2. Extend WorkflowRunner
**File:** `src/vellum/workflows/runner/runner.py`

- Add `trigger_event: Optional[dict] = None` parameter to `__init__`
- In initialization (lines 188-200):
  - Detect if workflow has integration triggers via `self.workflow.get_trigger_classes()`
  - If trigger_event provided, process it via trigger's `process_event()` method
  - Create OutputReferences for each trigger output field
  - Inject trigger outputs into `self._initial_state.meta.node_outputs`
- Add validation:
  - Error if trigger_event provided but no integration trigger in workflow
  - Error if multiple integration triggers in workflow (unsupported for now)
  - Error if integration trigger in workflow but no trigger_event provided

### 3. Add helper methods to BaseWorkflow
**File:** `src/vellum/workflows/workflows/base.py`

- `get_trigger_classes() -> Iterator[Type[BaseTrigger]]`: Iterate through subgraphs and collect all trigger classes
- `get_integration_trigger() -> Optional[Type[IntegrationTrigger]]`: Return the single integration trigger if present, error if multiple
- `_create_trigger_output_references(trigger_class: Type[IntegrationTrigger]) -> Dict[OutputReference, Any]`: Create OutputReference instances for each field in trigger.Outputs

## Phase 2: Testing

### 4. Update existing test
**File:** `tests/workflows/slack_trigger_workflow/`

- Modify `ProcessMessageNode` to actually access `SlackTrigger.Outputs.message`
- Update `test_slack_trigger_workflow__basic_execution` to:
  - Create realistic Slack event payload
  - Call `workflow.run(trigger_event=slack_event)`
  - Assert that node receives and processes the trigger output correctly

### 5. Add comprehensive integration tests
**Directory:** `tests/workflows/integration_trigger_execution/`

- Test successful execution with SlackTrigger event
- Test error when trigger_event missing
- Test error when trigger_event provided but no trigger in workflow
- Test that trigger outputs are accessible in nodes
- Test workflow with both ManualTrigger and IntegrationTrigger (multiple entry points)

### 6. Add apollo_bot test
**File:** `apollo_bot/test_workflow.py`

- Add test that actually runs apollo_bot with mock Slack event
- Verify the workflow executes end-to-end with trigger outputs

## Phase 3: Documentation & Examples

### 7. Update apollo_bot ProcessMessageNode
**File:** `apollo_bot/nodes/process_message.py`

- Remove placeholder comment
- Actually implement accessing SlackTrigger.Outputs.message

### 8. Add example/documentation
- Create simple example showing trigger execution pattern
- Update docstrings in IntegrationTrigger and SlackTrigger with runtime execution examples

## Branch Strategy
- Create new branch: `feature/apo-1836-integration-trigger-runtime-execution`
- Branch from: `feature/apo-1833-create-integration-trigger-for-slack-message-trigger` (current branch)

## Key Technical Details
- Trigger outputs stored in `state.meta.node_outputs` as `Dict[OutputReference, Any]`
- OutputReference.resolve() already handles lookup in node_outputs
- Trigger outputs injected before workflow execution begins
- No changes needed to serialization/codegen (already done in APO-1833)
