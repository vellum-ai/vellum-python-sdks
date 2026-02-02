import { ValueGenerationError } from "./errors";

import { VELLUM_WORKFLOW_DEFINITION_PATH } from "src/constants";
import { AstNode } from "src/generators/extensions/ast-node";
import { BoolInstantiation } from "src/generators/extensions/bool-instantiation";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { DictInstantiation } from "src/generators/extensions/dict-instantiation";
import { FloatInstantiation } from "src/generators/extensions/float-instantiation";
import { IntInstantiation } from "src/generators/extensions/int-instantiation";
import { ListInstantiation } from "src/generators/extensions/list-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { NoneInstantiation } from "src/generators/extensions/none-instantiation";
import { Reference } from "src/generators/extensions/reference";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { Writer } from "src/generators/extensions/writer";

interface VellumIntegrationToolData {
  type: "VELLUM_INTEGRATION";
  provider: string | null | undefined;
  integration_name: string | null | undefined;
  name: string | null | undefined;
  description: string | null | undefined;
  toolkit_version?: string | null | undefined;
}

function isVellumIntegrationToolData(value: Record<string, unknown>): boolean {
  return (
    value.type === "VELLUM_INTEGRATION" &&
    (typeof value.provider === "string" ||
      value.provider === null ||
      value.provider === undefined) &&
    (typeof value.integration_name === "string" ||
      value.integration_name === null ||
      value.integration_name === undefined) &&
    (typeof value.name === "string" ||
      value.name === null ||
      value.name === undefined) &&
    (typeof value.description === "string" ||
      value.description === null ||
      value.description === undefined) &&
    (typeof value.toolkit_version === "string" ||
      value.toolkit_version === null ||
      value.toolkit_version === undefined)
  );
}

function toVellumIntegrationToolData(
  value: Record<string, unknown>
): VellumIntegrationToolData {
  return {
    type: "VELLUM_INTEGRATION",
    provider: value.provider as string | null | undefined,
    integration_name: value.integration_name as string | null | undefined,
    name: value.name as string | null | undefined,
    description: value.description as string | null | undefined,
    toolkit_version: value.toolkit_version as string | null | undefined,
  };
}

export class Json extends AstNode {
  private readonly astNode: AstNode;

  constructor(value: unknown) {
    super();

    // Validate that value is JSON serializable
    try {
      JSON.stringify(value);
    } catch {
      throw new ValueGenerationError("Value is not JSON serializable");
    }

    this.astNode = this.generateAstNode(value);
    this.inheritReferences(this.astNode);
  }

  private generateAstNode(value: unknown): AstNode {
    if (value === null || value === undefined) {
      return new NoneInstantiation();
    }

    if (typeof value === "string") {
      return new StrInstantiation(value);
    }

    if (typeof value === "number") {
      if (Number.isInteger(value)) {
        return new IntInstantiation(value);
      }
      return new FloatInstantiation(value);
    }

    if (typeof value === "boolean") {
      return new BoolInstantiation(value);
    }

    if (Array.isArray(value)) {
      return new ListInstantiation(
        value.map((item) => {
          const jsonValue = new Json(item);
          this.inheritReferences(jsonValue);
          return jsonValue;
        }),
        {
          endWithComma: true,
        }
      );
    }

    if (typeof value === "object") {
      // Check if this is a VellumIntegrationToolDefinition
      const objValue = value as Record<string, unknown>;
      if (isVellumIntegrationToolData(objValue)) {
        return this.generateVellumIntegrationToolDefinition(
          toVellumIntegrationToolData(objValue)
        );
      }

      const entries = Object.entries(value).map(([key, val]) => {
        const jsonValue = new Json(val);
        this.inheritReferences(jsonValue);

        return {
          key: new StrInstantiation(key),
          value: jsonValue,
        };
      });
      return new DictInstantiation(entries, {
        endWithComma: true,
      });
    }

    throw new ValueGenerationError(
      `Unsupported JSON value type: ${typeof value}`
    );
  }

  private generateVellumIntegrationToolDefinition(
    integrationTool: VellumIntegrationToolData
  ): AstNode {
    const args: MethodArgument[] = [
      new MethodArgument({
        name: "provider",
        value: new StrInstantiation(integrationTool.provider ?? "COMPOSIO"),
      }),
      new MethodArgument({
        name: "integration_name",
        value: new StrInstantiation(
          integrationTool.integration_name ?? "UNKNOWN"
        ),
      }),
      new MethodArgument({
        name: "name",
        value: new StrInstantiation(integrationTool.name ?? "UNKNOWN"),
      }),
      new MethodArgument({
        name: "description",
        value: new StrInstantiation(integrationTool.description ?? ""),
      }),
    ];

    if (integrationTool.toolkit_version != null) {
      args.push(
        new MethodArgument({
          name: "toolkit_version",
          value: new StrInstantiation(integrationTool.toolkit_version),
        })
      );
    }

    const astNode = new ClassInstantiation({
      classReference: new Reference({
        name: "VellumIntegrationToolDefinition",
        modulePath: VELLUM_WORKFLOW_DEFINITION_PATH,
      }),
      arguments_: args,
    });

    this.inheritReferences(astNode);
    return astNode;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}
