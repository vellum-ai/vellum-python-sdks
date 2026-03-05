import { describe, expect, it } from "vitest";

import { PythonFile } from "src/generators/extensions/protected-python-file";
import { Reference } from "src/generators/extensions/reference";

describe("PythonFile import writing", () => {
  it("should relativize imports within the same module tree", () => {
    const ref = new Reference({
      name: "Inputs",
      modulePath: ["my_project", "inputs"],
    });

    const file = new PythonFile({
      path: ["my_project", "workflow", "nodes", "my_node"],
      rootModulePath: ["my_project", "workflow"],
      statements: [],
      imports: [ref],
    });

    const output = file.toString();

    expect(output).toContain("from ...inputs import Inputs");
    expect(output).not.toContain("my_project");
  });

  it("should NOT relativize imports from a sibling sub-package that only shares the top-level package", () => {
    const externalRef = new Reference({
      name: "MyHelper",
      modulePath: ["org", "shared", "utils", "helpers"],
    });

    const file = new PythonFile({
      path: [
        "org",
        "app",
        "support",
        "my_workflow",
        "workflow",
        "nodes",
        "my_node",
      ],
      rootModulePath: ["org", "app", "support", "my_workflow", "workflow"],
      statements: [],
      imports: [externalRef],
    });

    const output = file.toString();

    expect(output).toContain("from org.shared.utils.helpers import MyHelper");
    expect(output).not.toMatch(/\.{4,}/);
  });
});
