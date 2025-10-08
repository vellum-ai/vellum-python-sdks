## Current Objective
Add integration test fixtures for ManualTrigger codegen support in PR #2704 (APO-1852)

## Progress Summary
- Rebased PR #2704 on main to get updated serialization format (triggers at root level)
- Created `simple_manual_trigger_workflow` integration test fixture with Python code and JSON display data
- Fixed serialization format to match Django backend schema expectations

## Active Work
PR #2704 ready with complete ManualTrigger codegen support - all 32 integration tests passing

## Key Decisions & Context
- Serialization format changed in main: `triggers` array at root level, not `trigger` in workflow_raw_data
- Format: `{"triggers": [{"id": "...", "type": "MANUAL", "attributes": []}], "workflow_raw_data": {...}}`
- Module paths in fixtures must omit "ee" prefix for proper test matching
- TypeScript codegen in `ee/codegen/src/generators/graph-attribute.ts` prepends triggers using >> operator

## Next Steps
1. Monitor CI for PR #2704 to ensure all checks pass
2. Address any reviewer feedback on the PR
3. Consider adding more complex trigger fixtures (multiple entrypoints, conditional nodes)

## Important Files
- `ee/codegen_integration/fixtures/simple_manual_trigger_workflow/` (new fixture)
- `ee/codegen/src/generators/graph-attribute.ts` (TypeScript codegen logic)
- `ee/codegen/src/types/vellum.ts` (WorkflowTrigger type)
- `ee/vellum_ee/workflows/display/workflows/base_workflow_display.py` (serialization logic)

## Open Questions/Blockers
- CI status pending - need to verify all tests pass in GitHub Actions
- Parent PR #2698 exists but focusing on #2704 independently as requested
