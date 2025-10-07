## Current Objective
Implement ManualTrigger support for workflow execution, starting with serialization, codegen, then run/stream integration.

## Progress Summary
- Merged PR #2664 (APO-1832) containing BaseTrigger and ManualTrigger foundation into feature branch
- Renamed branch from `feature/integrations-triggers` to `feature/manual-trigger`
- Analyzed existing workflow execution flow and trigger implementation
- Reviewed Linear issues: APO-1836 (run/stream), APO-1837 (serialization), APO-1838 (codegen), APO-1833-1835 (future integration triggers)

## Active Work
Planning implementation order for ManualTrigger support. Ready to begin APO-1837 (serialization).

## Key Decisions & Context
- ManualTrigger replaces entrypoint node pattern (`graph = ManualTrigger >> MyNode` vs `graph = MyNode`)
- ManualTrigger doesn't change runtime behavior - makes implicit entrypoint explicit
- Node-level triggers already exist (`BaseNode.Trigger`) with serialization - this is workflow-level triggers
- Current execution: `workflow.graph` → `get_entrypoints()` → `WorkflowRunner._entrypoints` → starts execution
- Serialization/codegen must come before run/stream support to define JSON structure and roundtrip testing
- PR #2664 implementation: `BaseTrigger` metaclass with `>>` operator, `TriggerEdge`, graph integration

## Next Steps
1. **APO-1837**: Implement serialization for triggers
   - Define JSON structure for workflow-level triggers
   - Update `BaseWorkflowDisplay` to serialize trigger edges
   - Add tests in `ee/vellum_ee/workflows/display/tests/workflow_serialization/`
2. **APO-1838**: Implement codegen for triggers
   - Update TypeScript codegen to read trigger info from JSON
   - Generate `ManualTrigger >>` syntax
   - Add tests in `ee/codegen/src/__test__/`
3. **APO-1836**: Run/stream support (mainly for integration triggers later)

## Important Files
- `src/vellum/workflows/triggers/base.py` - BaseTrigger implementation
- `src/vellum/workflows/triggers/manual.py` - ManualTrigger implementation
- `src/vellum/workflows/edges/trigger_edge.py` - TriggerEdge class
- `src/vellum/workflows/graph/graph.py` - Graph with trigger edge support
- `src/vellum/workflows/graph/tests/test_graph.py` - Trigger graph tests
- `src/vellum/workflows/workflows/base.py` - BaseWorkflow (get_entrypoints at line 366-367)
- `src/vellum/workflows/runner/runner.py` - WorkflowRunner (sets _entrypoints at line 200)
- `ee/vellum_ee/workflows/display/` - Serialization code
- `ee/codegen/` - TypeScript codegen

## Open Questions/Blockers
None - ready to proceed with APO-1837 serialization implementation.
