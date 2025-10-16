# TDD Plan: Migrate VellumIntegrationTrigger from Factory to Inheritance Pattern

## Goal
Refactor `VellumIntegrationTrigger` to use **inheritance-only** pattern with required event attributes:

**New API:**
```python
class SlackNewMessageTrigger(VellumIntegrationTrigger):
    provider = VellumIntegrationProviderType.COMPOSIO
    integration_name = "SLACK"
    slug = "slack_new_message"
    trigger_nano_id = "abc123"

    # Required: declare event attributes with types
    event_attributes = {
        "message": str,
        "user": str,
        "timestamp": float,
        "channel": str,
    }

    # Optional: filter which events match this trigger
    filter_attributes = {"channel": "C123456"}
```

## Test-Driven Development Approach

Each test below is designed to **fail first** (red), then we implement the fix (green), then refactor if needed.

---

## Test 1: Metaclass recognizes inheritance classes for attribute references ✅

**Status:** ✅ COMPLETE

**What it tests:** Metaclass creates dynamic references for inheritance-based trigger classes.

**Implementation:** Updated `VellumIntegrationTriggerMeta.__getattribute__` to detect inheritance classes by checking for required configuration attributes rather than class name prefix.

---

## Test 2: Event attributes declaration is required

**Status:** 🔴 Not Started

**Test:**
```python
def test_inheritance_requires_event_attributes():
    """Inheritance classes must declare event_attributes."""

    # This should fail - no event_attributes declared
    with pytest.raises(TypeError, match="event_attributes"):
        class BadTrigger(VellumIntegrationTrigger):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "SLACK"
            slug = "slack_new_message"
            trigger_nano_id = "test_123"
            # Missing event_attributes!

    # This should work
    class GoodTrigger(VellumIntegrationTrigger):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_123"
        event_attributes = {
            "message": str,
            "user": str,
        }

    assert GoodTrigger.event_attributes == {"message": str, "user": str}
```

**Why it fails:** No validation currently requires `event_attributes` to be declared.

**Fix:** Add `__init_subclass__` to validate that subclasses define `event_attributes` as a dict with type values.

---

## Test 3: Event attributes create references automatically

**Status:** 🔴 Not Started

**Test:**
```python
def test_event_attributes_create_references():
    """Declared event_attributes automatically create TriggerAttributeReference."""

    class SlackTrigger(VellumIntegrationTrigger):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_123"
        event_attributes = {
            "message": str,
            "user": str,
        }

    # Should auto-create references from event_attributes
    assert isinstance(SlackTrigger.message, TriggerAttributeReference)
    assert isinstance(SlackTrigger.user, TriggerAttributeReference)
    assert SlackTrigger.message.types == (str,)

    # Undeclared attributes should raise AttributeError
    with pytest.raises(AttributeError):
        _ = SlackTrigger.undefined_attribute
```

**Why it fails:** Metaclass `__new__` doesn't create references for declared event_attributes.

**Fix:** Update `VellumIntegrationTriggerMeta.__new__` to automatically create `TriggerAttributeReference` objects for each attribute in `event_attributes`.

---

## Test 4: Filter attributes work correctly

**Status:** 🔴 Not Started

**Test:**
```python
def test_filter_attributes():
    """Filter attributes are optional and used for event filtering."""

    class SlackTrigger(VellumIntegrationTrigger):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_123"
        event_attributes = {"message": str}
        filter_attributes = {"channel": "C123456"}

    exec_config = SlackTrigger.to_exec_config()
    assert exec_config.filter_attributes == {"channel": "C123456"}

    # filter_attributes is optional
    class SlackTriggerNoFilter(VellumIntegrationTrigger):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_456"
        event_attributes = {"message": str}

    exec_config2 = SlackTriggerNoFilter.to_exec_config()
    assert exec_config2.filter_attributes == {}
```

**Why it fails:** Code currently uses `attributes` instead of `filter_attributes`.

**Fix:**
- Rename `attributes` → `filter_attributes` in `VellumIntegrationTrigger`
- Update `to_exec_config()` to use `filter_attributes`
- Update `ComposioIntegrationTriggerExecConfig` to have `filter_attributes` field

---

## Test 5: Stable attribute IDs based on semantic identity

**Status:** 🔴 Not Started

**Test:**
```python
def test_attribute_ids_use_semantic_identity():
    """Attribute IDs based on trigger config, not class name."""

    class Trigger1(VellumIntegrationTrigger):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_123"
        event_attributes = {"message": str}

    class Trigger2(VellumIntegrationTrigger):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_123"
        event_attributes = {"message": str}

    # Same config = same IDs, regardless of class name
    assert Trigger1.message.id == Trigger2.message.id
```

**Why it fails:** Currently may use class name in ID generation.

**Fix:** Ensure attribute IDs are generated from semantic identity `(provider, integration_name, slug, attribute_name)` not class name.

---

## Test 6: Workflow serialization

**Status:** 🔴 Not Started

**Test:**
```python
def test_serialize_workflow_with_inheritance_trigger():
    """Workflow with inheritance trigger serializes correctly."""

    class SlackTrigger(VellumIntegrationTrigger):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_123"
        event_attributes = {"message": str}
        filter_attributes = {"channel": "C123"}

    class SimpleNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result = SlackTrigger.message

        def run(self) -> Outputs:
            return self.Outputs()

    class TestWorkflow(BaseWorkflow):
        graph = SlackTrigger >> SimpleNode

    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    serialized = workflow_display.serialize()

    assert "triggers" in serialized["workflow_raw_data"]
    triggers = serialized["workflow_raw_data"]["triggers"]
    assert len(triggers) == 1
    assert triggers[0]["type"] == "COMPOSIO_INTEGRATION_TRIGGER"
```

**Why it fails:** Serialization code may not handle `VellumIntegrationTrigger` subclasses.

**Fix:** Update `_serialize_workflow_trigger()` in `base_workflow_display.py` to handle `VellumIntegrationTrigger` subclasses.

---

## Step 7: Remove Factory Pattern Code

**Status:** 🔴 Not Started

**Tasks:**
- Remove `for_trigger()` classmethod
- Remove `_trigger_class_cache`
- Remove `_freeze_attributes()`
- Simplify metaclass (remove factory-specific checks)
- Update docstrings

---

## Step 8: Remove Factory Pattern Tests

**Status:** 🔴 Not Started

**Tasks:**
- Delete `test_vellum_integration_trigger.py` (all factory tests)
- Keep only `test_vellum_integration_trigger_inheritance.py`

---

## Step 9: Update Usage in Codebase

**Status:** 🔴 Not Started

**Tasks:**
- Search for `VellumIntegrationTrigger.for_trigger(`
- Replace with inheritance pattern
- Update any documentation/examples

---

## Progress Tracking

- [x] Test 1: Metaclass recognizes inheritance classes
- [ ] Test 2: Event attributes declaration required
- [ ] Test 3: Event attributes create references automatically
- [ ] Test 4: Filter attributes work correctly
- [ ] Test 5: Stable attribute IDs
- [ ] Test 6: Serialization
- [ ] Step 7: Delete factory pattern code
- [ ] Step 8: Delete factory pattern tests
- [ ] Step 9: Update factory usage in codebase

## Key Design Decisions

### Required Event Attributes
- `event_attributes: Dict[str, Type]` must be declared on each trigger class
- Types are preserved for validation and documentation
- Metaclass automatically creates `TriggerAttributeReference` for each

### Optional Filter Attributes
- `filter_attributes: Dict[str, Any]` for filtering which events match
- Optional - defaults to empty dict if not provided
- JSON-serializable values only

### Serialization Strategy
- Serialize to `ComposioIntegrationTriggerExecConfig`
- Include: provider, integration_name, slug, trigger_nano_id, filter_attributes, event_attributes
- Class name not serialized (user-chosen, not semantic)
- Codegen regenerates class definitions from config
