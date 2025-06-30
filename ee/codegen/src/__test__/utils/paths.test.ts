import { workflowContextFactory } from "src/__test__/helpers";
import { WorkflowContext } from "src/context/workflow-context";
import { CodeResourceDefinition } from "src/types/vellum";
import { getGeneratedNodeModuleInfo } from "src/utils/paths";

describe("getGeneratedNodeModuleInfo", () => {
  let workflowContext: WorkflowContext;

  beforeEach(() => {
    workflowContext = workflowContextFactory({ moduleName: "my_project" });
  });

  const testCases: [
    {
      nodeDefinition?: CodeResourceDefinition | undefined;
      nodeLabel: string;
    },
    {
      expectedModuleName: string;
      expectedNodeClassName: string;
      expectedModulePath: string[];
    }
  ][] = [
    // No node definition defined
    [
      { nodeLabel: "My Node" },
      {
        expectedModuleName: "my_node",
        expectedModulePath: ["my_project", "nodes", "my_node"],
        expectedNodeClassName: "MyNode",
      },
    ],
    // Simple node definition is defined
    [
      {
        nodeLabel: "My Node",
        nodeDefinition: {
          module: ["my_project", "nodes", "my_node"],
          name: "MyNode",
        },
      },
      {
        expectedModuleName: "my_node",
        expectedModulePath: ["my_project", "nodes", "my_node"],
        expectedNodeClassName: "MyNode",
      },
    ],
    // Node definition containing an adornment is defined
    [
      {
        nodeLabel: "My Node",
        nodeDefinition: {
          module: ["my_project", "nodes", "my_node", "MyNode", "<adornment>"],
          name: "TryNode",
        },
      },
      {
        expectedModuleName: "my_node",
        expectedModulePath: ["my_project", "nodes", "my_node"],
        expectedNodeClassName: "MyNode",
      },
    ],
    // Node definition containing multiple adornments is defined
    [
      {
        nodeLabel: "My Node",
        nodeDefinition: {
          module: [
            "my_project",
            "nodes",
            "my_node",
            "MyNode",
            "<adornment>",
            "RetryNode",
            "<adornment>",
          ],
          name: "TryNode",
        },
      },
      {
        expectedModuleName: "my_node",
        expectedModulePath: ["my_project", "nodes", "my_node"],
        expectedNodeClassName: "MyNode",
      },
    ],
  ] as const;

  it.each(testCases)(
    "should derive the correct node module info",
    ({ nodeDefinition, nodeLabel }, expected) => {
      const { modulePath, moduleName, nodeClassName } =
        getGeneratedNodeModuleInfo({
          workflowContext,
          nodeDefinition,
          nodeLabel,
        });
      const { expectedModuleName, expectedNodeClassName, expectedModulePath } =
        expected;

      expect(moduleName).toEqual(expectedModuleName);
      expect(nodeClassName).toEqual(expectedNodeClassName);
      expect(modulePath).toEqual(expectedModulePath);
    }
  );
});
