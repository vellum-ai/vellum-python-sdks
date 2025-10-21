# PR Split Plan: VellumIntegrationTrigger Codegen Support (Revised)

## Analysis Summary

**Branch**: `feature/add-vellum-integration-trigger-codegen`
**Base**: `main`
**Total commits**: 10
**Total changes**: 14 files (602 insertions, 94 deletions)

This feature adds TypeScript codegen support for custom `VellumIntegrationTrigger` subclasses, enabling workflows to generate proper imports and references for integration triggers like `SlackMessageTrigger`.

## Simplified 3-PR Strategy

After reviewing the commits and changes, the most logical split is:

---

### PR #1: Core VellumIntegrationTrigger Codegen Implementation
**Branch**: `feature/integration-trigger-codegen-core`
**Commits to cherry-pick**: `08bd8d35`, `d4acb36b`, `f5cee16b`, `8bfdf137`, `a9c79250`

**Files** (9):
- `ee/vellum_ee/workflows/display/workflows/base_workflow_display.py` (serialization logic)
- `ee/vellum_ee/workflows/display/tests/workflow_serialization/test_vellum_integration_trigger_serialization.py` (new)
- `ee/codegen/src/types/vellum.ts` (WorkflowTrigger union type)
- `ee/codegen/src/serializers/vellum.ts` (basic serializer)
- `ee/codegen/src/utils/triggers.ts` (getTriggerClassInfo utility)
- `ee/codegen/src/generators/graph-attribute.ts` (graph generation)
- `ee/codegen/src/generators/workflow-value-descriptor-reference/trigger-attribute-workflow-reference.ts`
- `ee/codegen/src/__test__/workflow-value-descriptor-reference/trigger-attribute-workflow-reference.test.ts` (basic tests)
- `ee/codegen/src/__test__/workflow-value-descriptor-reference/__snapshots__/trigger-attribute-workflow-reference.test.ts.snap`

**Description**: Implements complete codegen support for VellumIntegrationTrigger subclasses including:
- Python serialization of class_name and module_path
- TypeScript WorkflowTrigger discriminated union type
- Codegen logic for generating trigger imports and references
- Integration trigger attribute reference generation
- Comprehensive serialization tests
- All TypeScript and mypy type errors resolved

**Why this grouping**: This is the core feature implementation with all necessary fixes to make it work. It's a complete, working unit that adds the new capability.

---

### PR #2: Bug Fixes - Trigger/Entrypoint Relationship & Workflow Traversal
**Branch**: `feature/trigger-entrypoint-bugfixes`
**Commits to cherry-pick**: `ca9fef9b`, `d4f22713`, `d5ad86a9`

**Files** (5):
- `ee/vellum_ee/workflows/display/workflows/base_workflow_display.py` (skip entrypoint when triggers exist)
- `ee/vellum_ee/workflows/display/tests/workflow_serialization/test_manual_trigger_serialization.py` (entrypoint tests)
- `ee/vellum_ee/workflows/display/tests/workflow_serialization/test_vellum_integration_trigger_serialization.py` (ID consistency test)
- `ee/codegen/src/generators/graph-attribute.ts` (handle workflows without entrypoint)
- `ee/codegen/src/__test__/graph-attribute.test.ts` (tests for workflows without entrypoint)

**Description**: Fixes two architectural bugs discovered during implementation:
1. **Trigger/Entrypoint Bug**: Triggers were creating both trigger AND entrypoint nodes. Fixed to skip entrypoint when triggers exist, as triggers themselves serve as the entry point.
2. **Workflow Traversal Bug**: Codegen failed on workflows without entrypoint nodes. Fixed to find root nodes (nodes with no incoming edges) and start BFS from there.
3. **Regression Test**: Adds validation test for trigger ID consistency to prevent hash formula bugs.

**Why this grouping**: These are bug fixes that affect trigger behavior. They build on PR #1 but fix edge cases and architectural issues.

---

### PR #3: Type Safety Refactor - WorkflowTriggerType Enum Migration
**Branch**: `feature/trigger-type-enum-migration`
**Commits to cherry-pick**: `1081418f`, `cb5aba4c`

**Files** (7):
- `ee/codegen/src/types/vellum.ts` (add WorkflowTriggerType enum)
- `ee/codegen/src/serializers/vellum.ts` (discriminated union with enum)
- `ee/codegen/src/utils/triggers.ts` (use enum, remove null checks)
- `ee/codegen/src/generators/graph-attribute.ts` (use enum)
- `ee/codegen/src/__test__/utils/triggers.test.ts` (new unit tests)
- `ee/codegen/src/__test__/workflow-value-descriptor-reference/trigger-attribute-workflow-reference.test.ts` (enum usage)
- `ee/codegen/src/__test__/helpers/node-data-factories.ts` (enum usage in factories)

**Description**: Refactors TypeScript code for better type safety:
- Introduces `WorkflowTriggerType` enum to replace string literals
- Updates discriminated union serializer to use enum values
- Removes unnecessary null checks (TypeScript type guards ensure required fields exist)
- Simplifies `getTriggerClassInfo()` implementation
- Adds comprehensive unit tests for trigger utilities

**Why this grouping**: This is a pure refactoring PR that improves type safety without changing functionality. Safe to merge after the core feature and bug fixes are in.

---

### Snapshot Updates (Included in Each PR)
**Note**: Snapshot files will be updated in each PR as needed rather than a separate PR:
- PR #1: Initial snapshots for integration trigger tests
- PR #2: Updated snapshots for entrypoint-less workflows
- PR #3: No new snapshots (refactor doesn't change output)

---

## Dependency Graph

```
PR #1 (Core Feature)
  ↓
PR #2 (Bug Fixes)
  ↓
PR #3 (Type Safety Refactor)
```

## Merge Strategy

### Sequential Merges (Required)
1. **PR #1** → Core feature implementation (must merge first)
2. **PR #2** → Bug fixes building on core feature
3. **PR #3** → Type safety improvements (safest to merge last)

### No Parallel Merges
Given the file overlap (especially `base_workflow_display.py` and `graph-attribute.ts`), sequential merging is required to avoid conflicts.

### Review Focus
- **PR #1**: Core implementation, type definitions, serialization logic, test coverage
- **PR #2**: Bug fix correctness, edge case handling, regression test validity
- **PR #3**: Type safety improvements, enum migration completeness, no behavior changes

## File Size & Complexity

- **PR #1**: 9 files, ~420 lines (Medium complexity - new feature)
- **PR #2**: 5 files, ~180 lines (Low complexity - focused bug fixes)
- **PR #3**: 7 files, ~150 lines (Low complexity - pure refactor)

All PRs are reasonably sized for review.

## Risk Assessment

### PR #1 (Medium Risk)
- Adds new functionality
- Well-tested with comprehensive integration tests
- Type errors resolved
- Risk: New serialization contract between Python/TypeScript

### PR #2 (Low-Medium Risk)
- Bug fixes to existing behavior
- TDD approach with regression tests
- Risk: Architectural change in entrypoint handling

### PR #3 (Low Risk)
- Pure refactoring, no behavior change
- Type safety improvements
- Comprehensive test coverage
- Risk: Very low, enum migration is straightforward

## Success Criteria

Each PR must:
- [ ] Pass all tests (Python and TypeScript)
- [ ] Pass mypy type checking
- [ ] Pass TypeScript compilation (`tsc --noEmit`)
- [ ] Include appropriate test coverage
- [ ] Have clear, descriptive commit messages
- [ ] Reference this overall effort in PR description

## Backup & Recovery

- **Backup branch**: `original-branch-backup` ✓ Created
- **Original branch**: `feature/add-vellum-integration-trigger-codegen` (preserved)
- **Recovery**: `git checkout original-branch-backup` if needed
