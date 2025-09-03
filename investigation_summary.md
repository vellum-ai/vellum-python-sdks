# Investigation Summary: Graph.empty() Issue with MapNode/RetryNode

## Problem Description
7 test failures related to MapNode and RetryNode with error messages:
- "Missing required Workflow input: item" (MapNode tests)
- "Missing required Workflow input: attempt_number" (RetryNode tests)

## Root Cause Analysis

### Key Issue
The codegen was changed to generate `Graph.empty()` instead of proper graph structures for workflows with no edges, which breaks MapNode and RetryNode subworkflow input generation.

### Specific Changes Made
1. **ee/codegen/src/generators/graph-attribute.ts:1137-1150** - Changed from returning `python.TypeInstantiation.none()` to `Graph.empty()` for empty graphs
2. **ee/codegen/src/generators/workflow.ts:630-642** - Removed early return when `edges.length === 0`, allowing GraphAttribute creation to proceed
3. **src/vellum/workflows/graph/graph.py:100-102** - Added `Graph.empty()` static method

### Problem Flow
1. When a workflow has a single MapNode/RetryNode with no edges (e.g., `graph = MappableNode`)
2. The codegen now generates `graph = Graph.empty()` instead of `graph = MappableNode`
3. This breaks the subworkflow input generation mechanism that MapNode/RetryNode depend on
4. MapNode needs `SubworkflowInputs.item`, `SubworkflowInputs.index`, etc.
5. RetryNode needs `SubworkflowInputs.attempt_number`

### Test Cases Affected
- `src/vellum/workflows/nodes/core/map_node/tests/test_node.py::test_map_node__use_parent_inputs_and_state`
- `src/vellum/workflows/nodes/core/retry_node/tests/test_node.py` (3 tests)
- `tests/workflows/basic_map_node_annotation/tests/test_workflow.py::test_run_workflow__happy_path`
- `tests/workflows/basic_retry_node_annotation/tests/test_workflow.py::test_run_workflow__happy_path`
- `tests/workflows/basic_retry_node_delay_annotation/tests/test_workflow.py::test_run_workflow__happy_path`

### Snapshot Evidence
In `ee/codegen/src/__test__/__snapshots__/workflow.test.ts.snap:72`, shows:
```python
graph = Graph.empty()
unused_graphs = {FinalOutput}
```

## Technical Details

### MapNode/RetryNode Architecture
- MapNode defines `class SubworkflowInputs(BaseInputs)` with fields like `item`, `index`, `items`
- RetryNode defines similar with `attempt_number`
- These nodes create subworkflows that expect these special inputs
- The subworkflow input generation relies on proper graph structure, not `Graph.empty()`

### GraphAttribute Logic
- `generateGraphMutableAst()` starts with `{ type: "empty" }`
- Processes edges via BFS from entrypoint
- If no edges exist, stays empty
- `getGraphAttributeAstNode()` converts empty to `Graph.empty()`

## Current Status
- Built codegen TypeScript successfully
- Identified the exact files and line numbers causing the issue
- Understanding the flow from codegen → graph generation → subworkflow inputs

## Planned Next Steps

### 1. Fix the GraphAttribute Logic
The core issue is in `ee/codegen/src/generators/graph-attribute.ts`. Need to modify `generateGraphMutableAst()` to handle the case where there are nodes that should be part of the graph even without edges.

**Approach**: Check if there are entrypoint-connected nodes that should be included directly when no edges exist.

### 2. Alternative: Revert the Empty Graph Change
Consider reverting the change from `None` to `Graph.empty()` in graph-attribute.ts:1137-1150, but understand why the original change was needed.

### 3. Test the Fix
Once fixed, verify:
```bash
make test file=src/vellum/workflows/nodes/core/map_node/tests/test_node.py
make test file=src/vellum/workflows/nodes/core/retry_node/tests/test_node.py
make test file=tests/workflows/basic_map_node_annotation/tests/test_workflow.py
# etc.
```

### 4. Update Snapshots if Needed
```bash
cd ee/codegen && npm run test:update
```

## Key Files to Focus On

### Primary Fix Location
- `ee/codegen/src/generators/graph-attribute.ts` - Lines ~70-90 in `generateGraphMutableAst()`
- May need to check for standalone nodes that should be included in graph

### Modified Files from Git Status
- `ee/codegen/src/generators/graph-attribute.ts` (the Graph.empty() change)
- `ee/codegen/src/generators/workflow.ts` (removed early return)
- `src/vellum/workflows/graph/graph.py` (added Graph.empty() method)

### Test Files for Validation
- All the failing test paths mentioned above

## Context for Next LLM
The investigation is at the point where the root cause is clearly identified. The issue is that single-node graphs (common with MapNode/RetryNode) are being converted to `Graph.empty()` which breaks their subworkflow input mechanism. The fix likely involves modifying the graph generation logic to properly handle standalone nodes that should be included in the main graph structure.
