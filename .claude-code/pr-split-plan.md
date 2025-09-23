# PR Split Plan: VellumIntegration Feature

## Analysis of Current Changes

The current branch `feat/vellum-integration-node-implementation` contains implementation for Vellum Integration support in the workflows SDK. The changes can be clearly separated into two logical components:

1. **VellumIntegrationService Foundation** - Core service implementation
2. **VellumIntegrationNode Implementation** - Node and utilities for tool execution

## Changed Files Overview

### Client/API Changes (Auto-generated - removed Composio references):
- Removed Composio-related types and client methods
- Updated client initialization and imports

### New Implementation Files:
- `src/vellum/workflows/integrations/vellum_integration_service.py` - Core service
- `src/vellum/workflows/integrations/tests/test_vellum_integration_service.py` - Service tests
- `src/vellum/workflows/nodes/displayable/tool_calling_node/tests/test_vellum_integration_node.py` - Node tests
- `src/vellum/workflows/utils/tests/test_vellum_integration_functions.py` - Function compilation tests

### Modified Files:
- `src/vellum/workflows/nodes/displayable/tool_calling_node/utils.py` - Added VellumIntegration support
- `src/vellum/workflows/nodes/displayable/bases/inline_prompt_node/node.py` - Added VellumIntegration tool support
- `src/vellum/workflows/utils/functions.py` - Updated to handle VellumIntegration tools
- `src/vellum/workflows/integrations/__init__.py` - Export new components
- Various codegen files for TypeScript support

## PR Splitting Strategy

### PR 1: VellumIntegrationService Foundation
**Branch**: `feat/vellum-integration-service`
**Purpose**: Introduce the core VellumIntegrationService class without any node implementation

**Files**:
1. `src/vellum/workflows/integrations/vellum_integration_service.py`
2. `src/vellum/workflows/integrations/tests/test_vellum_integration_service.py`
3. `src/vellum/workflows/integrations/__init__.py` (partial - only VellumIntegrationService export)
4. Client changes (removal of Composio references) - these are foundational cleanup
5. `CLAUDE.md` - documentation update

**Rationale**: This establishes the service layer that will be used by the node. It's a clean, standalone component.

### PR 2: VellumIntegrationNode Implementation
**Branch**: `feat/vellum-integration-node`
**Purpose**: Add the VellumIntegrationNode and related utilities for tool execution

**Files**:
1. `src/vellum/workflows/nodes/displayable/tool_calling_node/tests/test_vellum_integration_node.py`
2. `src/vellum/workflows/nodes/displayable/tool_calling_node/utils.py` (VellumIntegration additions)
3. `src/vellum/workflows/nodes/displayable/bases/inline_prompt_node/node.py` (VellumIntegration support)
4. `src/vellum/workflows/utils/functions.py` (VellumIntegration handling)
5. `src/vellum/workflows/utils/tests/test_vellum_integration_functions.py`
6. `src/vellum/workflows/utils/tests/test_functions.py` (removed Composio tests)
7. `src/vellum/workflows/integrations/__init__.py` (VellumIntegrationNode export)
8. Codegen/TypeScript files for node support

**Rationale**: This builds on top of the service to provide the actual workflow node functionality.

## Dependencies

- **PR 1** has no dependencies and can be merged independently
- **PR 2** depends on PR 1 (needs VellumIntegrationService to be available)

## Merge Strategy

**Sequential**:
1. Merge PR 1 first (VellumIntegrationService)
2. Rebase PR 2 if needed, then merge

Both PRs are cohesive and independently reviewable. PR 1 establishes the foundation, while PR 2 adds the user-facing node functionality.

## Review Focus Areas

### PR 1:
- Service implementation correctness
- API integration approach
- Test coverage for service methods

### PR 2:
- Node implementation pattern consistency
- Tool compilation logic
- Integration with existing tool calling infrastructure
- TypeScript codegen compatibility
