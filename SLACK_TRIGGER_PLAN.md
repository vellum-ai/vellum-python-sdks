# SlackTrigger Implementation Plan

## Overview
Implement the first integration trigger for workflows - SlackTrigger - which allows workflows to be initiated from Slack events (messages, app mentions, etc.). This follows the established pattern from ManualTrigger but adds trigger outputs that downstream nodes can reference.

## Context
- **Linear Issue**: [APO-1833](https://linear.app/vellum/issue/APO-1833/create-integration-trigger-for-on-slack-message-trigger) - Create Integration Trigger for on Slack Message Trigger
- **Related Issues**:
  - APO-1836 - Support workflow.run and workflow.stream of non-manual triggers
  - APO-1856 - Support workflow.run and workflow.stream of manual triggers
- **Project**: Triggers for Native Integrations
- **Current State**: ManualTrigger is fully implemented with graph syntax, serialization, and codegen support. No integration triggers exist yet.

## Key Requirements

### From Project Plan
```python
class SlackMessageTrigger:
    class Outputs:
        message: str      # The message text
        channel: str      # Slack channel ID
        user: str         # User who sent the message
        timestamp: str    # Message timestamp
        thread_ts: str    # Thread timestamp (if threaded)
```

### Design Decisions
1. **IntegrationTrigger Base Class**: Create a base class for all integration triggers (Slack, Email, etc.)
2. **Trigger Outputs**: Unlike ManualTrigger, integration triggers produce outputs that nodes can reference
3. **Configuration**: Triggers need configuration (OAuth tokens, webhook URLs, etc.)
4. **Naming**: Use `SlackTrigger` (not `SlackMessageTrigger`) for brevity

## Implementation Phases

### Phase 1: Foundation - Core Trigger Classes
**Goal**: Create the base IntegrationTrigger class and SlackTrigger implementation

#### 1.1 Create IntegrationTrigger Base Class
**File**: `src/vellum/workflows/triggers/integration.py`

```python
from abc import ABC
from typing import ClassVar, Optional
from vellum.workflows.triggers.base import BaseTrigger
from vellum.workflows.outputs.base import BaseOutputs

class IntegrationTrigger(BaseTrigger, ABC):
    """
    Base class for integration-based triggers (Slack, Email, etc.).

    Integration triggers:
    - Are initiated by external events (webhooks, API calls)
    - Produce outputs that downstream nodes can reference
    - Require configuration (auth, webhooks, etc.)
    """

    class Outputs(BaseOutputs):
        """Base outputs for integration triggers."""
        pass

    # Configuration that can be set at runtime
    config: ClassVar[Optional[dict]] = None

    @classmethod
    def process_event(cls, event_data: dict) -> "IntegrationTrigger.Outputs":
        """
        Process incoming webhook/event data and return trigger outputs.
        To be implemented by subclasses.
        """
        raise NotImplementedError
```

**Tests**: `src/vellum/workflows/triggers/tests/test_integration.py`
- Test IntegrationTrigger cannot be instantiated directly (ABC)
- Test Outputs class inheritance

#### 1.2 Create SlackTrigger Class
**File**: `src/vellum/workflows/triggers/slack.py`

```python
from typing import Optional
from vellum.workflows.triggers.integration import IntegrationTrigger

class SlackTrigger(IntegrationTrigger):
    """
    Trigger for Slack events (messages, mentions, reactions, etc.).

    Examples:
        # Basic Slack message trigger
        class MyWorkflow(BaseWorkflow):
            graph = SlackTrigger >> ProcessMessageNode

        # Access trigger outputs in nodes
        class ProcessMessageNode(BaseNode):
            class Outputs(BaseNode.Outputs):
                response = SlackTrigger.Outputs.message

    Outputs:
        message: str - The message text from Slack
        channel: str - Slack channel ID where message was sent
        user: str - User ID who sent the message
        timestamp: str - Message timestamp
        thread_ts: Optional[str] - Thread timestamp if message is in thread
        event_type: str - Type of Slack event (e.g., "message", "app_mention")
    """

    class Outputs(IntegrationTrigger.Outputs):
        message: str
        channel: str
        user: str
        timestamp: str
        thread_ts: Optional[str]
        event_type: str

    @classmethod
    def process_event(cls, event_data: dict) -> "SlackTrigger.Outputs":
        """
        Parse Slack webhook payload into trigger outputs.

        Args:
            event_data: Slack event payload from webhook

        Returns:
            SlackTrigger.Outputs with parsed data
        """
        # Extract from Slack's event structure
        event = event_data.get("event", {})

        return cls.Outputs(
            message=event.get("text", ""),
            channel=event.get("channel", ""),
            user=event.get("user", ""),
            timestamp=event.get("ts", ""),
            thread_ts=event.get("thread_ts"),
            event_type=event.get("type", "message"),
        )
```

**Tests**: `src/vellum/workflows/triggers/tests/test_slack.py`
- Test SlackTrigger can be used in graph syntax: `SlackTrigger >> Node`
- Test process_event parses Slack payload correctly
- Test Outputs class has correct fields
- Test thread_ts is optional

#### 1.3 Update Trigger Exports
**File**: `src/vellum/workflows/triggers/__init__.py`

```python
from vellum.workflows.triggers.base import BaseTrigger
from vellum.workflows.triggers.manual import ManualTrigger
from vellum.workflows.triggers.integration import IntegrationTrigger
from vellum.workflows.triggers.slack import SlackTrigger

__all__ = ["BaseTrigger", "ManualTrigger", "IntegrationTrigger", "SlackTrigger"]
```

### Phase 2: Type Definitions
**Goal**: Add type support for triggers with outputs

#### 2.1 Add Trigger Output Types
**File**: `src/vellum/workflows/types/definition.py`

Add trigger-related types:
```python
# Add to existing file
from typing import Literal

TriggerOutputType = Literal["STRING", "NUMBER", "JSON", "BOOLEAN"]

class TriggerOutputDefinition:
    name: str
    type: TriggerOutputType
    required: bool
```

**Tests**: `src/vellum/workflows/types/tests/test_definition.py`
- Test TriggerOutputDefinition serialization
- Test trigger output type validation

### Phase 3: Runtime Execution Support
**Goal**: Support workflow execution initiated by SlackTrigger

#### 3.1 Extend WorkflowRunner to Handle Trigger Inputs
**File**: `src/vellum/workflows/runner/runner.py`

Modify to accept trigger event data:
```python
class WorkflowRunner:
    def __init__(
        self,
        workflow,
        inputs=None,
        trigger_event: Optional[dict] = None,  # NEW
        # ... existing params
    ):
        # If trigger_event provided, process it through the trigger
        if trigger_event and workflow.get_trigger():
            trigger_cls = workflow.get_trigger()
            trigger_outputs = trigger_cls.process_event(trigger_event)
            # Make trigger outputs available to nodes
            # ... implementation details
```

#### 3.2 Add Trigger Output Resolution
**File**: `src/vellum/workflows/references/trigger_output.py` (NEW)

Similar to OutputReference but for trigger outputs:
```python
class TriggerOutputReference:
    """Reference to a trigger's output that can be used in nodes."""

    def __init__(self, trigger_cls, output_name):
        self.trigger_cls = trigger_cls
        self.output_name = output_name
```

#### 3.3 Workflow Methods for Trigger Execution
**File**: `src/vellum/workflows/workflows/base.py`

Add methods to support trigger-initiated execution:
```python
class BaseWorkflow:
    @classmethod
    def get_trigger(cls) -> Optional[Type[BaseTrigger]]:
        """Get the workflow's trigger if one is defined."""
        # Extract from graph
        pass

    def run_from_trigger(
        self,
        trigger_event: dict,
        **kwargs
    ) -> TerminalWorkflowEvent:
        """
        Execute workflow from a trigger event.

        Args:
            trigger_event: Event data from the trigger (e.g., Slack webhook payload)
            **kwargs: Additional arguments passed to run()
        """
        return self.run(trigger_event=trigger_event, **kwargs)
```

**Tests**: `tests/workflows/slack_trigger_workflow/tests/test_workflow.py`
- Test workflow.run_from_trigger() with Slack event
- Test trigger outputs are accessible in nodes
- Test SlackTrigger >> Node execution
- Test SlackTrigger >> {NodeA, NodeB} execution

### Phase 4: Serialization Support
**Goal**: Serialize SlackTrigger workflows for storage and UI display

#### 4.1 Add SlackTrigger Serialization
**File**: `ee/vellum_ee/workflows/display/triggers/slack.py` (NEW)

```python
from vellum.workflows.types.core import JsonObject

class SlackTriggerDisplay:
    @staticmethod
    def serialize(trigger_class) -> JsonObject:
        return {
            "type": "SLACK_MESSAGE",
            "id": str(trigger_class.__id__),
            "attributes": [],
            "outputs": [
                {"name": "message", "type": "STRING"},
                {"name": "channel", "type": "STRING"},
                {"name": "user", "type": "STRING"},
                {"name": "timestamp", "type": "STRING"},
                {"name": "thread_ts", "type": "STRING"},
                {"name": "event_type", "type": "STRING"},
            ],
        }
```

#### 4.2 Update Trigger Serializer
**File**: `ee/vellum_ee/workflows/display/base.py`

Update to handle SlackTrigger:
```python
def serialize_trigger(trigger_class):
    from vellum.workflows.triggers import ManualTrigger, SlackTrigger

    if trigger_class == ManualTrigger:
        return ManualTriggerDisplay.serialize(trigger_class)
    elif trigger_class == SlackTrigger:
        return SlackTriggerDisplay.serialize(trigger_class)
    else:
        raise ValueError(f"Unknown trigger type: {trigger_class.__name__}")
```

**Tests**: `ee/vellum_ee/workflows/display/tests/workflow_serialization/test_slack_trigger_serialization.py`
- Test SlackTrigger serialization structure
- Test outputs are included in serialization
- Test trigger type is "SLACK_MESSAGE"
- Test multiple entrypoints with SlackTrigger
- Test round-trip serialization

### Phase 5: Codegen Support
**Goal**: Generate TypeScript code for SlackTrigger workflows

#### 5.1 Add SlackTrigger to TypeScript Types
**File**: `ee/codegen/src/types/vellum.ts`

```typescript
export type WorkflowTriggerType = "MANUAL" | "SLACK_MESSAGE";

export interface SlackTriggerOutputs {
  message: string;
  channel: string;
  user: string;
  timestamp: string;
  thread_ts?: string;
  event_type: string;
}
```

#### 5.2 Update Trigger Code Generation
**File**: `ee/codegen/src/generators/graph-attribute.ts`

Add SlackTrigger mapping:
```typescript
function getTriggerClassInfo(triggerType: string) {
  switch (triggerType) {
    case "MANUAL":
      return { className: "ManualTrigger", modulePath: MANUAL_TRIGGER_MODULE_PATH };
    case "SLACK_MESSAGE":
      return { className: "SlackTrigger", modulePath: SLACK_TRIGGER_MODULE_PATH };
    default:
      throw new Error(`Unknown trigger type: ${triggerType}`);
  }
}
```

#### 5.3 Add Trigger Constants
**File**: `ee/codegen/src/constants.ts`

```typescript
export const SLACK_TRIGGER_MODULE_PATH = ["vellum", "workflows", "triggers", "slack"];
```

**Tests**: `ee/codegen/src/__test__/graph-attribute.test.ts`
- Test SlackTrigger >> Node codegen
- Test trigger import generation
- Test trigger outputs in generated code

#### 5.4 Create Integration Test Fixture
**Directory**: `ee/codegen_integration/fixtures/slack_trigger_workflow/`

Create complete workflow example with SlackTrigger:
```
slack_trigger_workflow/
├── __init__.py
├── code/
│   ├── __init__.py
│   ├── inputs.py
│   ├── workflow.py
│   └── nodes/
│       ├── __init__.py
│       ├── process_message.py
│       └── send_response.py
└── slack_trigger_workflow.json  # Display data
```

**Tests**: Integration test verifies codegen round-trip

### Phase 6: Testing & Documentation
**Goal**: Comprehensive testing and documentation

#### 6.1 Integration Tests
**File**: `tests/workflows/slack_trigger_workflow/` (complete example)

Create realistic workflow:
```python
class SlackWorkflow(BaseWorkflow):
    graph = SlackTrigger >> ProcessMessageNode >> SendResponseNode

    class Outputs:
        response_text = SendResponseNode.Outputs.text
```

Test scenarios:
- Full workflow execution from Slack event
- Trigger output access in multiple nodes
- Error handling for malformed Slack payloads
- Threading scenarios (thread_ts)

#### 6.2 Unit Tests Summary
Ensure coverage for:
- `src/vellum/workflows/triggers/integration.py` - 100%
- `src/vellum/workflows/triggers/slack.py` - 100%
- Serialization - 100%
- Codegen - 100%

#### 6.3 Documentation Updates
**File**: `src/vellum/workflows/triggers/slack.py`
- Comprehensive docstring with examples
- Document all output fields
- Usage patterns

## File Structure Summary

### New Files
```
src/vellum/workflows/triggers/
├── integration.py                     # NEW - IntegrationTrigger base class
├── slack.py                           # NEW - SlackTrigger implementation
└── tests/
    ├── test_integration.py            # NEW
    └── test_slack.py                  # NEW

src/vellum/workflows/references/
└── trigger_output.py                  # NEW - TriggerOutputReference

ee/vellum_ee/workflows/display/triggers/
└── slack.py                           # NEW - SlackTrigger serialization

ee/vellum_ee/workflows/display/tests/workflow_serialization/
└── test_slack_trigger_serialization.py  # NEW

ee/codegen_integration/fixtures/
└── slack_trigger_workflow/            # NEW - Complete example
    ├── code/
    └── slack_trigger_workflow.json

tests/workflows/slack_trigger_workflow/  # NEW - Integration tests
├── workflow.py
├── nodes/
└── tests/
```

### Modified Files
```
src/vellum/workflows/triggers/__init__.py    # Add exports
src/vellum/workflows/types/definition.py     # Add trigger output types
src/vellum/workflows/runner/runner.py        # Support trigger events
src/vellum/workflows/workflows/base.py       # Add trigger methods
ee/vellum_ee/workflows/display/base.py       # Add SlackTrigger serialization
ee/codegen/src/types/vellum.ts               # Add SlackTrigger types
ee/codegen/src/generators/graph-attribute.ts # Add SlackTrigger codegen
ee/codegen/src/constants.ts                  # Add trigger constants
ee/codegen/src/__test__/graph-attribute.test.ts  # Add tests
```

## Dependencies
- No new external dependencies required
- Uses existing Pydantic for output validation
- Uses existing serialization framework

## Success Criteria
- [ ] SlackTrigger can be used in graph syntax: `SlackTrigger >> Node`
- [ ] Trigger outputs accessible in nodes: `SlackTrigger.Outputs.message`
- [ ] Workflow can execute from Slack webhook payload
- [ ] Serialization includes trigger outputs
- [ ] TypeScript codegen generates correct imports and syntax
- [ ] All tests pass (unit + integration)
- [ ] Test coverage >= 90% for new code
- [ ] Documentation complete with examples
- [ ] CI/CD pipeline passes
- [ ] Backwards compatible (ManualTrigger workflows unaffected)

## Testing Strategy
```bash
# Run trigger tests
make test file=src/vellum/workflows/triggers/tests/

# Run integration tests
make test file=tests/workflows/slack_trigger_workflow/

# Run serialization tests
make test file=ee/vellum_ee/workflows/display/tests/workflow_serialization/test_slack_trigger_serialization.py

# Run codegen tests
cd ee/codegen && npm test

# Run full test suite
make test-ci
```

## Open Questions & Design Decisions

### 1. Trigger Output Reference Pattern
**Question**: How should nodes reference trigger outputs?

**Option A** (Recommended): Direct reference
```python
class MyNode(BaseNode):
    class Outputs:
        msg = SlackTrigger.Outputs.message
```

**Option B**: Through workflow inputs
```python
# Trigger outputs automatically become workflow inputs
class MyNode(BaseNode):
    class Outputs:
        msg = Workflow.Inputs.slack_message
```

**Decision**: Use Option A - keeps trigger outputs explicit and clear

### 2. Configuration Management
**Question**: How to handle Slack OAuth tokens, webhook secrets?

**Options**:
- Environment variables (recommended for MVP)
- Runtime configuration passed to workflow
- Centralized secrets management

**Decision**: Start with environment variables, add configuration support in later phase

### 3. Event Filtering
**Question**: Should SlackTrigger support filtering (e.g., only certain channels)?

**Decision**: Defer to post-MVP. For now, filtering happens in workflow logic

### 4. Multiple Triggers
**Question**: Can a workflow have both ManualTrigger and SlackTrigger?

**Decision**: Yes, supported via set syntax: `graph = {ManualTrigger >> NodeA, SlackTrigger >> NodeB}`

## Migration & Backwards Compatibility
- **No breaking changes**: Existing ManualTrigger workflows continue working
- **Additive only**: All changes are new functionality
- **Explicit opt-in**: Workflows must explicitly use SlackTrigger

## Future Enhancements (Post-MVP)
1. Additional Slack events (reactions, mentions, etc.)
2. Slack-specific nodes (send message, update message, etc.)
3. Email trigger (following same pattern)
4. Scheduled trigger
5. Generic webhook trigger
6. Trigger configuration UI
7. Trigger testing/debugging tools

## Reference Links
- Linear Issue: https://linear.app/vellum/issue/APO-1833/create-integration-trigger-for-on-slack-message-trigger
- ManualTrigger PR: #2704 (reference implementation)
- ManualTrigger Serialization: #2695
- Project Plan: (provided in context)
