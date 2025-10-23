# Trigger-to-Entrypoint Serialization Investigation

## Problem Statement

The TypeScript codegen tests are failing because the serialized workflow data doesn't properly represent how triggers connect to the first nodes in a workflow.

**Failing Tests:**
- `ee/codegen/src/__test__/graph-attribute.test.ts`:
  - "should generate correct graph when workflow has a manual trigger"
  - "should generate correct graph when workflow has a VellumIntegrationTrigger"

**Expected Output:** `ManualTrigger >> FirstNode >> SecondNode`
**Actual Output:** `Graph.empty()`

## How This Was Discovered

While fixing eslint errors in PR #2825, we removed unused `entrypointNode` variables from tests (commit dae69dc4). This revealed a fundamental gap in the serialization contract:

**The test has:**
- Triggers defined in `workflowContext.triggers`
- Nodes: `[firstNode, secondNode]` (no ENTRYPOINT node)
- Edges: `[[firstNode, secondNode]]` (no edge from trigger to firstNode)

**The question:** How does the codegen know to connect the trigger to firstNode?

**The answer:** It doesn't. The codegen currently requires an ENTRYPOINT node.

## Root Cause Analysis

### Current System Architecture

The codegen graph generation works as follows:

1. **Find entrypoint node** (`workflow-context.ts:289-309`):
   ```typescript
   public tryGetEntrypointNode(): EntrypointNode | null {
     const entrypointNodes = this.workflowRawData.nodes.filter(
       (n): n is EntrypointNode => n.type === "ENTRYPOINT"
     );
     // Returns the ENTRYPOINT node or null
   }
   ```

2. **Get edges from entrypoint** (`workflow-context.ts:310-318`):
   ```typescript
   public getEntrypointNodeEdges(): WorkflowEdge[] {
     const entrypointNode = this.tryGetEntrypointNode();
     if (!entrypointNode) return [];
     return this.workflowRawData.edges.filter(
       (edge) => edge.sourceNodeId === entrypointNode.id
     );
   }
   ```

3. **Build graph from edges** (`graph-attribute.ts:83-180`):
   - Gets entrypoint edges
   - If no edges, returns `{type: "empty"}` (line 117-119)
   - Builds graph via BFS traversal
   - **ONLY IF graph is non-empty**, prepends trigger reference (lines 161-177)

### Why Tests Are Failing

Commit `dae69dc4` removed ENTRYPOINT nodes from tests with this comment:
```typescript
// When a trigger is present, it IS the entry point - no entrypoint node needed
```

But the codegen doesn't support this yet:
- No ENTRYPOINT node → `tryGetEntrypointNode()` returns null
- No entrypoint → `getEntrypointNodeEdges()` returns `[]`
- No edges → graph becomes `{type: "empty"}`
- Empty graph → trigger prepending logic never runs → output is `Graph.empty()`

### The Core Issue

**There's a mismatch between the Python runtime and TypeScript codegen:**

**Python Runtime (APO-1836):**
- Triggers ARE the entrypoints
- WorkflowRunner gets entrypoints from subgraph.entrypoints
- No ENTRYPOINT node needed in the graph definition

**TypeScript Codegen:**
- Still expects ENTRYPOINT nodes in serialized data
- Uses ENTRYPOINT node as a proxy to find initial edges
- Replaces ENTRYPOINT with trigger class in the generated code

## Historical Context

**Commit dae69dc4** (Fix P1 trigger routing issues):
- Removed ENTRYPOINT nodes from test data
- Added comment saying triggers are the entrypoints
- **But didn't update the codegen to handle this**

**Earlier (commit aae0b677)**:
- Tests included ENTRYPOINT nodes with IDs matching trigger IDs
- Edges went: `[entrypointNode, firstNode], [firstNode, secondNode]`
- This worked because codegen could find the entrypoint

## Relevant Code Locations

### TypeScript Codegen
- `ee/codegen/src/context/workflow-context/workflow-context.ts:289-318`
  - `tryGetEntrypointNode()`: Finds ENTRYPOINT nodes
  - `getEntrypointNodeEdges()`: Gets edges from ENTRYPOINT node

- `ee/codegen/src/generators/graph-attribute.ts:83-180`
  - `generateGraphMutableAst()`: Main graph generation logic
  - Lines 110-119: Gets entrypoint edges, returns empty if none
  - Lines 161-177: Prepends trigger to graph (only if graph non-empty)

- `ee/codegen/src/types/vellum.ts:789-833`
  - `WorkflowTrigger`: Trigger type definitions
  - `WorkflowVersionExecConfig`: Contains `triggers` array
  - `WorkflowRawData`: Contains nodes and edges (but not triggers directly)

### Python Runtime
- `src/vellum/workflows/runner/runner.py:254-348`
  - `_process_trigger()`: Handles trigger validation and routing
  - Gets entrypoints from workflow subgraphs

### Test Files
- `ee/codegen/src/__test__/graph-attribute.test.ts:1052-1159`
  - Lines 1052-1102: Manual trigger test
  - Lines 1104-1159: VellumIntegrationTrigger test
  - Both currently fail with `Graph.empty()`

## Options for Fixing

### Option 1: Keep ENTRYPOINT Nodes (Backward Compatible)
**Approach:** Revert test changes, keep ENTRYPOINT nodes as proxy for triggers

**Pros:**
- No codegen changes needed
- Maintains existing serialization contract
- Works with current infrastructure

**Cons:**
- ENTRYPOINT node is redundant (trigger is already the entrypoint)
- Requires extra node in serialized data
- Conceptually confusing (why have both trigger and entrypoint?)

**Implementation:**
- Revert changes to graph-attribute.test.ts
- Keep ENTRYPOINT nodes in serialized workflow data
- Codegen replaces ENTRYPOINT with trigger in generated code

### Option 2: Add Trigger Entrypoints Metadata
**Approach:** Add `entrypoints: string[]` field to WorkflowTrigger

**Pros:**
- Clean separation: triggers declare which nodes they connect to
- Explicit connection information
- No redundant nodes

**Cons:**
- Changes serialization contract
- Requires updates to serializers/deserializers
- Need to handle backward compatibility

**Implementation:**
```typescript
export type WorkflowTrigger = {
  id: string;
  type: WorkflowTriggerType;
  attributes: NodeAttribute[];
  entrypoints: string[]; // Node IDs this trigger connects to
  // ...
}
```

### Option 3: Infer from Edges with Trigger Source
**Approach:** Allow edges to reference trigger IDs as `sourceNodeId`

**Pros:**
- Uses existing edge structure
- Clear connection representation
- Natural extension of current model

**Cons:**
- Edges currently expect node IDs, not trigger IDs
- May confuse logic that assumes sourceNodeId is a node
- Need to update edge processing logic

**Implementation:**
```typescript
// Allow edges like:
{
  sourceNodeId: "trigger-1",  // Trigger ID, not node ID
  sourceHandleId: "...",
  targetNodeId: "first-node",
  targetHandleId: "..."
}
```

### Option 4: Infer from Graph Structure
**Approach:** When triggers exist, treat nodes with no incoming edges as trigger entrypoints

**Pros:**
- No serialization changes needed
- Works with current data structure
- Simple to implement

**Cons:**
- Implicit connection (hard to understand)
- Ambiguous when multiple triggers and multiple root nodes
- Doesn't specify which trigger connects to which nodes

**Implementation:**
- In `generateGraphMutableAst()`, when triggers exist:
  - Find all nodes with no incoming edges
  - Use those as starting points for graph traversal
  - Prepend trigger to the resulting graph

## Recommended Approach

~~**Option 2 (Add Trigger Entrypoints Metadata)** is the cleanest long-term solution:~~

**UPDATE: Implemented Option 3 (Infer from Edges with Trigger Source)** - simpler and more explicit:

1. **Trigger is first-class graph node:** No special metadata needed
2. **No synthetic edges:** Edges exist in serialized data
3. **More explicit:** Connection is clear in the graph structure
4. **Natural extension:** Uses existing edge model

**Implementation:**
1. Add edges where `sourceNodeId` is trigger ID, `targetNodeId` is first node
2. Update `getEntrypointNodeEdges()` to filter edges by trigger IDs
3. Maintain backward compatibility (fall back to ENTRYPOINT nodes)
4. Update tests to include trigger edges in serialized data

## Implementation Checklist

~~When implementing the fix:~~ **COMPLETED - Option 3 Implementation**

### 1. Test Updates
- [x] Update failing tests in `graph-attribute.test.ts`
- [x] Add edges from trigger to firstNode in test data
- [x] Verify snapshots match expected output

### 2. Codegen Updates
- [x] Update `getEntrypointNodeEdges()` in `workflow-context.ts`
  - Filter edges where `sourceNodeId` matches trigger IDs
  - Fall back to ENTRYPOINT node lookup for backward compatibility

- [x] Update `generateGraphMutableAst()` in `graph-attribute.ts`
  - Simplified to call `getEntrypointNodeEdges()` unconditionally
  - No changes needed (already handles trigger sources)

- [x] Update `addEdgeToGraph()` in `graph-attribute.ts`
  - Detect trigger sources and treat them like ENTRYPOINT nodes

- [x] Update edge filtering in `workflow.ts`
  - Exclude edges from triggers (like ENTRYPOINT nodes)

### 3. Integration Testing
- [x] Test with ManualTrigger - PASS
- [x] Test with IntegrationTrigger (SlackMessageTrigger) - PASS
- [x] Test backward compatibility with ENTRYPOINT nodes - PASS
- [x] Full test suite - 601/602 tests passing

## Success Criteria ✅ ACHIEVED

~~The fix is complete when:~~ **ALL CRITERIA MET:**

1. ✅ Both failing tests pass:
   - "should generate correct graph when workflow has a manual trigger"
   - "should generate correct graph when workflow has a VellumIntegrationTrigger"

2. ✅ Generated graph output matches expected:
   - `ManualTrigger >> FirstNode >> SecondNode`
   - `SlackMessageTrigger >> FirstNode >> SecondNode`

3. ✅ No ENTRYPOINT nodes required in test data (edges use trigger IDs directly)

4. ✅ Backward compatibility maintained (old serialized data with ENTRYPOINT nodes still works)

## Related Files to Review

**Tests:**
- `ee/codegen/src/__test__/graph-attribute.test.ts` (failing tests)
- `ee/codegen/src/__test__/helpers/node-data-factories.ts` (entrypointNodeDataFactory)
- `ee/codegen/src/__test__/helpers/edge-data-factories.ts` (edgesFactory)

**Codegen:**
- `ee/codegen/src/context/workflow-context/workflow-context.ts`
- `ee/codegen/src/generators/graph-attribute.ts`
- `ee/codegen/src/types/vellum.ts`

**Python (for serialization):**
- Search for where `WorkflowVersionExecConfig` is created
- Look for trigger serialization logic

## Questions to Answer

1. Where in the Python codebase is `WorkflowVersionExecConfig` created and serialized?
2. How do we determine which nodes are trigger entrypoints when serializing?
3. Should we support multiple triggers with different entrypoints in the same workflow?
4. What's the backward compatibility story for existing serialized workflows?

## Next Steps

1. Decide on implementation approach (recommend Option 2)
2. Find Python serialization code
3. Implement TypeScript type and codegen changes
4. Update tests
5. Verify end-to-end functionality

---

**Branch:** `investigation/trigger-entrypoint-serialization`
**Related PR:** #2825 (APO-1836 - run workflow with trigger)
**Date:** 2025-10-22
