# vellum-ai/vellum-python-sdks - Style Guide & Best Practices

## Introduction

This is a **living** style guide for the [`vellum-ai/vellum-python-sdks`](https://github.com/vellum-ai/vellum-python-sdks) repository. Its purpose is to document actionable, specific, and practical coding conventions, best practices, and architectural patterns that have emerged through code review and team discussion. This guide evolves as the codebase and team practices change—**contributions and updates are welcome**.

---

## Code Style Guidelines

### General Formatting

- **Follow [PEP 8](https://peps.python.org/pep-0008/)** for Python code style.
- Use 4 spaces for indentation.
- Limit lines to 100 characters where possible.
- Use [Black](https://black.readthedocs.io/en/stable/) for automatic code formatting.

### Naming Conventions

- **Variables and functions**: `snake_case`
- **Classes**: `CamelCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Fields matching backend models**: Use the exact naming and pluralization as expected by the backend.

### Type Annotations

- Use type annotations for all public functions, methods, and class attributes.
- Prefer **specific types** as soon as they are available (e.g., `CancelSignal` instead of `Any`).

### Imports

- Group imports: standard library, third-party, local modules.
- Use absolute imports unless a relative import is required.

### Code Organization

- Move code to the most logical module or class as the codebase evolves.
- Prefer smaller, focused modules and classes.

---

## Best Practices

### 1. Schema and API Consistency

**Guideline:**
Always verify that any new or changed fields precisely match backend expectations (naming, pluralization, and placement).

**Why:**
Prevents runtime errors and ensures smooth integration with backend services.

**Good:**
```python
# Backend expects 'triggers' at the top level
data = {
    "triggers": [...],
    "actions": [...],
}
```

**Bad:**
```python
# Incorrect: field is singular and nested
data = {
    "trigger": {...},
    "actions": [...],
}
```

---

### 2. Test-Driven Development (TDD)

**Guideline:**
When fixing bugs or adding features, first write a test that fails on `main`, then implement the fix.

**Why:**
Ensures that the fix addresses the real issue and prevents regressions.

**Good:**
1. Add a test that fails due to the bug.
2. Make code changes to pass the test.
3. Commit both together.

**Bad:**
- Pushing a fix without a corresponding test.
- Writing tests only after the fix.

---

### 3. Error Handling and Messaging

**Guideline:**
Catch all relevant exceptions and provide clear, actionable, and differentiated error messages.

**Why:**
Improves debuggability and user experience.

**Good:**
```python
try:
    module = load_module(path)
except ImportError as e:
    raise WorkflowInitializationException(f"Module import failed: {e}")
except Exception as e:
    raise WorkflowInitializationException(f"Unexpected failure while loading module: {e}")
```

**Bad:**
```python
try:
    module = load_module(path)
except Exception:
    raise Exception("Error loading module")
```

---

### 4. Minimal, Necessary Fields

**Guideline:**
Only include fields in data models and serialized output that are required by the current schema or use case.

**Why:**
Reduces confusion and prevents backend errors.

**Good:**
```python
# Only include required fields
serialized = {
    "name": workflow.name,
    "triggers": workflow.triggers,
}
```

**Bad:**
```python
# Including unnecessary or unsupported fields
serialized = {
    "name": workflow.name,
    "triggers": workflow.triggers,
    "definition": workflow.definition,  # Not needed
}
```

---

### 5. Type Safety

**Guideline:**
Use specific types for function parameters and return values as soon as they're available.

**Why:**
Improves code reliability and maintainability.

**Good:**
```python
def run(cancel_signal: CancelSignal) -> None:
    ...
```

**Bad:**
```python
def run(cancel_signal: Any) -> None:
    ...
```

---

### 6. Value Inference

**Guideline:**
Infer values from existing structures (e.g., class names) where possible, rather than duplicating information.

**Why:**
Reduces redundancy and potential for inconsistencies.

**Good:**
```python
class WebhookTrigger(BaseTrigger):
    ...

def serialize(self):
    return {"type": self.__class__.__name__}
```

**Bad:**
```python
class WebhookTrigger(BaseTrigger):
    type = "webhook"

def serialize(self):
    return {"type": self.type}
```

---

### 7. Forward Compatibility and Extensibility

**Guideline:**
Design APIs and models to allow for future extensibility (e.g., support for user-defined triggers).

**Why:**
Prevents technical debt and makes it easier to add features later.

**Good:**
- Use serialization methods that can handle unknown or additional fields.
- Document extension points.

---

### 8. Code Cleanliness and Refactoring

**Guideline:**
Refactor and clean up code structure as you go, but clearly note when changes are deferred.

**Why:**
Maintains codebase health and avoids accumulating technical debt.

**Good:**
```python
# TODO: Move this logic to workflow_utils.py in a future PR
```

---

## Common Mistakes to Avoid

- **Schema mismatches:**
  Adding fields that are singular/pluralized incorrectly, or nested at the wrong level.

- **Unnecessary fields:**
  Serializing or exposing fields not required by the backend.

- **Generic error messages:**
  Using vague messages like `"Error occurred"` instead of specific, actionable ones.

- **Lack of test coverage:**
  Not writing tests for new features or edge cases before implementing fixes.

- **Hardcoding/duplicating information:**
  Not leveraging class structure or existing data to infer values.

- **Neglecting type annotations:**
  Using `Any` or omitting types when more specific types are available.

---

## Architecture & Design Patterns

- **Data Model Alignment:**
  Always mirror backend data models and contracts in Python representations.

- **Extensible Serialization:**
  Use methods that can be easily extended for future fields or types.

- **Single Responsibility Principle:**
  Each module/class/function should have a clear, focused responsibility.

- **Explicit Extension Points:**
  Document and design for areas likely to be extended (e.g., triggers, actions).

---

## Testing Guidelines

- **TDD:**
  Write a failing test before fixing a bug or implementing a new feature.

- **Test Coverage:**
  Cover all new code paths, especially edge cases and error handling.

- **Test Placement:**
  Place tests in the appropriate `tests/` subdirectory, mirroring the code structure.

- **Test Naming:**
  Use descriptive names that indicate what is being tested and under what conditions.

- **Regression Tests:**
  Add tests for any bug that is fixed to prevent future regressions.

---

## Security Considerations

- **Input Validation:**
  Validate all external inputs before processing.

- **Error Message Hygiene:**
  Avoid leaking sensitive information in error messages.

- **Dependency Management:**
  Keep dependencies up to date and avoid known-vulnerable versions.

---

## Performance Guidelines

- **Efficient Data Structures:**
  Use appropriate data structures for the task.

- **Avoid Unnecessary Computation:**
  Only compute or serialize what is required.

- **Batch Operations:**
  Where possible, batch API calls or data processing to minimize overhead.

---

## Code Review Checklist

- [ ] Are all new/changed fields aligned with backend/data model contracts?
- [ ] Are type annotations specific and up-to-date?
- [ ] Are error messages clear, actionable, and unique?
- [ ] Are only necessary fields serialized or exposed?
- [ ] Is there a failing test for each bug fix or new feature?
- [ ] Are values inferred from existing structures where possible?
- [ ] Is code organized in the most logical location?
- [ ] Are extension points and future-proofing considered?
- [ ] Are there no obvious security or performance issues?
- [ ] Are all relevant edge cases tested?

---

## References

- [PR: Schema field placement](https://github.com/vellum-ai/vellum-python-sdks/pull/XX) — Example of backend field alignment
- [PR: TDD for workflow lockfile](https://github.com/vellum-ai/vellum-python-sdks/pull/YY) — Example of writing failing test before fix
- [PR: Error message clarity](https://github.com/vellum-ai/vellum-python-sdks/pull/ZZ) — Example of improving error messages
- [PR: Type safety with CancelSignal](https://github.com/vellum-ai/vellum-python-sdks/pull/AA) — Example of updating to specific types

---

**This document is a living resource. If you encounter new patterns, anti-patterns, or best practices in your work or in code reviews, please propose updates to this guide.**
