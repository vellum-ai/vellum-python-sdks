# APO-1833: Integration Triggers Context

## Current Objective
Refactor integration triggers to use VellumIntegrationTrigger factory pattern (matching VellumIntegrationToolDefinition) instead of hardcoded trigger classes.

## Progress Summary
- Analyzed TDD at https://www.notion.so/vellum-ai/TDD-Integration-Triggers-2889035c57bd80f4a8ccf2d938436040
- Created comprehensive implementation plan aligned with backend architecture
- Created 4 Linear sub-issues: APO-1876 (Foundation), APO-1877 (Serialization), APO-1878 (Migration), APO-1879 (Codegen)
- Branch already exists: `feature/APO-1833-integration-triggers`

## Active Work
✅ **COMPLETED APO-1876 (Foundation)**: Created VellumIntegrationTrigger with factory pattern - all tests passing!

## Key Decisions & Context
- **Pure factory pattern** (Option A): No pre-defined trigger classes like SlackTrigger
- Users create triggers dynamically: `SlackNewMessage = VellumIntegrationTrigger.for_trigger("SLACK", "SLACK_NEW_MESSAGE")`
- True parity with VellumIntegrationToolDefinition pattern
- SlackTrigger class will be **removed entirely** (not a breaking change - not used in production yet)
- Exec config format from TDD: `ComposioIntegrationTriggerExecConfig` with provider/integration_name/trigger_name/attributes
- Integration triggers are configuration stored in backend; SDK provides factory for local development/testing

## Next Steps
**APO-1876 is complete! Ready for:**
1. APO-1877 (Serialization): Add VellumIntegrationTrigger serialization to WorkflowTriggerType enum
2. APO-1878 (Migration): Remove SlackTrigger and update all references
3. APO-1879 (Codegen): Integrate with code generation for deployment

## APO-1876 Implementation Summary
✅ Created `src/vellum/workflows/triggers/vellum_integration.py` with:
  - `VellumIntegrationTriggerMeta` metaclass for dynamic attribute discovery
  - `VellumIntegrationTrigger` base class with `for_trigger()` factory method
  - Support for dynamic attributes via custom `__getattribute__` override
  - Override of `to_trigger_attribute_values()` for proper state binding
✅ Created `src/vellum/workflows/types/trigger_exec_config.py` with:
  - `BaseIntegrationTriggerExecConfig` base class
  - `ComposioIntegrationTriggerExecConfig` for Composio provider
✅ Added `VellumIntegrationTriggerDefinition` to `src/vellum/workflows/types/definition.py`
✅ Extended `VellumIntegrationService.get_trigger_definition()` stub method
✅ Updated exports in `__init__.py` files
✅ Created comprehensive test suite (14 tests, all passing)
✅ Verified existing tests still pass (ManualTrigger, SlackTrigger)

## Important Files
**Current state:**
- `src/vellum/workflows/triggers/integration.py` - IntegrationTrigger base class
- `src/vellum/workflows/triggers/slack.py` - SlackTrigger (to be removed)
- `src/vellum/workflows/integrations/vellum_integration_service.py` - Service for tools
- `src/vellum/workflows/types/definition.py` - Tool definitions
- `src/vellum/workflows/constants.py` - VellumIntegrationProviderType enum
- `ee/vellum_ee/workflows/display/base.py` - WorkflowTriggerType enum, serialization

**Pattern reference (tools):**
- `src/vellum/workflows/nodes/displayable/tool_calling_node/utils.py:281-296` - VellumIntegrationNode
- `src/vellum/workflows/types/definition.py:171-183` - VellumIntegrationToolDefinition

## Open Questions/Blockers
None - ready to start implementation.
