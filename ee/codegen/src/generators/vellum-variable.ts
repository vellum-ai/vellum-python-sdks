import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { isNil } from "lodash";
import { VellumValue as VellumValueType } from "vellum-ai/api/types";

import { Field } from "./extensions";
import { OptionalType } from "./extensions/optional";

import { Writer } from "src/generators/extensions/writer";
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
  private readonly field: python.Field | Field;
  private readonly defaultRequired?: boolean;

  constructor({ variable, defaultRequired }: VellumVariable.Args) {
    super();

    const baseType = getVellumVariablePrimitiveType(variable.type);
    const name = variable.name ?? variable.key;
    this.defaultRequired = defaultRequired;

    // NULL type do not need to be optional
    // variable.required === false is used to indicate that the variable is optional
    // if required not defined, we use defaultRequired to determine if the variable is optional
    // See VellumVariable.defaultRequired for more information
    if (
      variable.type !== "NULL" &&
      (variable.required === false ||
        (variable.required === undefined && defaultRequired === false))
    ) {
      this.field = new Field({
        name,
        type: new OptionalType(baseType),
        initializer: variable.default
          ? this.generateInitializerIfDefault(variable)
          : python.TypeInstantiation.none(),
      });
    } else {
      this.field = new Field({
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

    // Check if the default type is ARRAY, JSON, or CHAT_HISTORY
    // Use Field(default_factory=...) for list types to avoid mutable default issues
    const isArrayType = variable.default.type === "ARRAY";
    const isJsonType = variable.default.type === "JSON";
    const isChatHistoryType = variable.default.type === "CHAT_HISTORY";

    // Also check if the variable type itself is a list type (CHAT_HISTORY or ARRAY)
    // and the default value is an empty array
    const isVariableListType =
      variable.type === "CHAT_HISTORY" || variable.type === "ARRAY";

    // Handle arrays: ARRAY, JSON with array values, and CHAT_HISTORY need Field(default_factory=list)
    if (
      ((isArrayType || isJsonType || isChatHistoryType) &&
        Array.isArray(variable.default.value)) ||
      (isVariableListType &&
        Array.isArray(variable.default.value) &&
        variable.default.value.length === 0)
    ) {
      // Use Field(default_factory=list) for empty lists
      // Use Field(default_factory=lambda: [...]) for non-empty lists
      const fieldReference = python.reference({
        name: "Field",
        modulePath: ["pydantic"],
      });
      this.addReference(fieldReference);

      const isEmpty = (variable.default.value as unknown[]).length === 0;
      const defaultFactoryValue = isEmpty
        ? python.reference({
            name: "list",
          })
        : python.lambda({
            body: new VellumValue({
              vellumValue: variable.default,
            }),
          });

      return python.instantiateClass({
        classReference: fieldReference,
        arguments_: [
          python.methodArgument({
            name: "default_factory",
            value: defaultFactoryValue,
          }),
        ],
      });
    }

    if (
      isJsonType &&
      variable.default.value !== null &&
      typeof variable.default.value === "object" &&
      !Array.isArray(variable.default.value)
    ) {
      // Use Field(default_factory=dict) for empty dicts
      // Use Field(default_factory=lambda: {...}) for non-empty dicts
      const fieldReference = python.reference({
        name: "Field",
        modulePath: ["pydantic"],
      });
      this.addReference(fieldReference);

      const isEmpty =
        Object.keys(variable.default.value as object).length === 0;
      const defaultFactoryValue = isEmpty
        ? python.reference({
            name: "dict",
          })
        : python.lambda({
            body: new VellumValue({
              vellumValue: variable.default,
            }),
          });

      return python.instantiateClass({
        classReference: fieldReference,
        arguments_: [
          python.methodArgument({
            name: "default_factory",
            value: defaultFactoryValue,
          }),
        ],
      });
    }

    // For non-empty defaults, use the regular VellumValue
    // If default.value is null, generate = None only for optional fields
    // Required fields should not have = None as default
    if (isNil(variable.default.value)) {
      const isOptional =
        variable.required === false ||
        (variable.required === undefined && this.defaultRequired === false);
      if (isOptional) {
        return python.TypeInstantiation.none();
      }
      // For required fields with null default, don't set an initializer
      return undefined;
    }
    return new VellumValue({
      vellumValue: variable.default,
    });
  }

  public write(writer: Writer): void {
    this.field.write(writer);
  }
}
