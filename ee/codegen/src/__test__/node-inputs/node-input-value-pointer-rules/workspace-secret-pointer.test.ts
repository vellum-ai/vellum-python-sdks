import { nodeContextFactory } from "src/__test__/helpers";
import { BaseNodeContext } from "src/context/node-context/base";
import { Writer } from "src/generators/extensions/writer";
import { WorkspaceSecretPointerRule } from "src/generators/node-inputs/node-input-value-pointer-rules/workspace-secret-pointer";
import { WorkflowDataNode } from "src/types/vellum";

describe("WorkspaceSecretPointer", () => {
  let writer: Writer;
  let nodeContext: BaseNodeContext<WorkflowDataNode>;

  beforeEach(async () => {
    writer = new Writer();
    nodeContext = await nodeContextFactory();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("should generate correct Python code", async () => {
    const workspaceSecretPointer = new WorkspaceSecretPointerRule({
      nodeContext,
      nodeInputValuePointerRule: {
        type: "WORKSPACE_SECRET",
        data: {
          type: "STRING",
          workspaceSecretId: "MY_SECRET",
        },
      },
    });

    workspaceSecretPointer.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should handle the the case where the workspace secret isn't yet specified", async () => {
    const workspaceSecretPointer = new WorkspaceSecretPointerRule({
      nodeContext,
      nodeInputValuePointerRule: {
        type: "WORKSPACE_SECRET",
        data: {
          type: "STRING",
          workspaceSecretId: undefined,
        },
      },
    });

    workspaceSecretPointer.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
