import { python } from "@fern-api/python-ast";
import { Type } from "@fern-api/python-ast/Type";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";
import { isNil } from "lodash";
import { VellumValue as VellumValueType } from "vellum-ai/api/types";

import { VellumValue } from "src/generators/vellum-variable-value";
import { getVellumVariablePrimitiveType } from "src/utils/vellum-variables";

type VellumVariableWithName = (
  | VellumValueType
  | { type: "NULL"; value?: null }
) &
  ({ name: string; key?: undefined } | { name?: undefined; key: string }) & {
    id: string;
    required?: boolean | null;
    default?: VellumValueType | null;
  };

// VellumVariable.defaultRequired:
// Prompt Inputs: required: undefined == required: true,
// Workflow Inputs: required: undefined == required: false
// Workflow Outputs: required: undefined == required: true
export declare namespace VellumVariable {
  interface Args {
    variable: VellumVariableWithName;
    defaultRequired?: boolean;
  }
}

export class VellumVariable extends AstNode {
  private readonly field: python.Field;

  constructor({ variable, defaultRequired }: VellumVariable.Args) {
    super();

    const baseType = getVellumVariablePrimitiveType(variable.type);
    const name = variable.name ?? variable.key;

    // NULL type do not need to be optional
    // variable.required === false is used to indicate that the variable is optional
    // if required not defined, we use defaultRequired to determine if the variable is optional
    // See VellumVariable.defaultRequired for more information
    if (
      variable.type !== "NULL" &&
      (variable.required === false ||
        (variable.required === undefined && defaultRequired === false))
    ) {
      this.field = python.field({
        name,
        type: Type.optional(baseType),
        initializer: variable.default
          ? this.generateInitializerIfDefault(variable)
          : python.TypeInstantiation.none(),
      });
    } else {
      this.field = python.field({
        name,
        type: baseType,
        initializer: variable.default
          ? this.generateInitializerIfDefault(variable)
          : undefined,
      });
    }

    this.inheritReferences(this.field);
  }

  private generateInitializerIfDefault(
    variable: VellumVariableWithName
  ): AstNode | undefined {
    if (!variable.default) {
      return variable.default == null
        ? python.TypeInstantiation.none()
        : undefined;
    }

    // Check if the default value is an empty list or empty dict
    // Use Field(default_factory=list) for empty lists to avoid mutable default issues
    // Use Field(default_factory=dict) for empty dicts to avoid mutable default issues
    const isEmptyList =
      Array.isArray(variable.default.value) &&
      variable.default.value.length === 0;
    const isEmptyDict =
      variable.default.value !== null &&
      typeof variable.default.value === "object" &&
      !Array.isArray(variable.default.value) &&
      Object.keys(variable.default.value).length === 0;

    if (isEmptyList) {
      // Use Field(default_factory=list) for empty lists
      const fieldReference = python.reference({
        name: "Field",
        modulePath: ["pydantic"],
      });
      this.addReference(fieldReference);

      return python.instantiateClass({
        classReference: fieldReference,
        arguments_: [
          python.methodArgument({
            name: "default_factory",
            value: python.reference({
              name: "list",
            }),
          }),
        ],
      });
    }

    if (isEmptyDict) {
      // Use Field(default_factory=dict) for empty dicts
      const fieldReference = python.reference({
        name: "Field",
        modulePath: ["pydantic"],
      });
      this.addReference(fieldReference);

      return python.instantiateClass({
        classReference: fieldReference,
        arguments_: [
          python.methodArgument({
            name: "default_factory",
            value: python.reference({
              name: "dict",
            }),
          }),
        ],
      });
    }

    // For non-empty defaults, use the regular VellumValue
    return !isNil(variable.default.value)
      ? new VellumValue({
          vellumValue: variable.default,
        })
      : undefined;
  }

  public write(writer: Writer): void {
    this.field.write(writer);
  }
}
