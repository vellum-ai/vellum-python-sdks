import { mkdir, readFile, rm } from "fs/promises";
import { join } from "path";

import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { mapNodeDataFactory } from "src/__test__/helpers/node-data-factories";
import { makeTempDir } from "src/__test__/helpers/temp-dir";
import { createNodeContext } from "src/context";
import { MapNodeContext } from "src/context/node-context/map-node";
import { MapNode } from "src/generators/nodes/map-node";

describe("MapNode", () => {
  let tempDir: string;

  beforeEach(async () => {
    tempDir = makeTempDir("map-node-test");
    await mkdir(tempDir, { recursive: true });
  });

  afterEach(async () => {
    await rm(tempDir, { recursive: true, force: true });
  });

  describe("basic", () => {
    beforeEach(async () => {
      const workflowContext = workflowContextFactory({
        absolutePathToOutputDirectory: tempDir,
        moduleName: "code",
      });
      const nodeData = mapNodeDataFactory();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as MapNodeContext;

      const node = new MapNode({
        workflowContext,
        nodeContext,
      });

      await node.persist();
    });

    it(`map node file`, async () => {
      expect(
        await readFile(
          join(tempDir, "code", "nodes", "map_node", "__init__.py"),
          "utf-8"
        )
      ).toMatchSnapshot();
    });

    it(`map node display file`, async () => {
      expect(
        await readFile(
          join(tempDir, "code", "display", "nodes", "map_node", "__init__.py"),
          "utf-8"
        )
      ).toMatchSnapshot();
    });
  });

  describe("with additional output", () => {
    beforeEach(async () => {
      const workflowContext = workflowContextFactory({
        absolutePathToOutputDirectory: tempDir,
        moduleName: "code",
      });
      const nodeData = mapNodeDataFactory({
        outputVariables: [
          {
            id: "edd5cfd5-6ad8-437d-8775-4b9aeb62a5fb",
            key: "first-output",
            type: "STRING",
          },
          {
            id: "edd5cfd5-6ad8-437d-8775-4b9aeb62a5fc",
            key: "second-output",
            type: "STRING",
          },
        ],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as MapNodeContext;

      const node = new MapNode({
        workflowContext,
        nodeContext,
      });

      await node.persist();
    });

    it(`map node file`, async () => {
      expect(
        await readFile(
          join(tempDir, "code", "nodes", "map_node", "__init__.py"),
          "utf-8"
        )
      ).toMatchSnapshot();
    });

    it(`map node display file`, async () => {
      expect(
        await readFile(
          join(tempDir, "code", "display", "nodes", "map_node", "__init__.py"),
          "utf-8"
        )
      ).toMatchSnapshot();
    });
  });
});
