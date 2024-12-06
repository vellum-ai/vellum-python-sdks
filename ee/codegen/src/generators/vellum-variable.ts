import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";
import { VellumValue as VellumValueType } from "vellum-ai/api/types";
import { VellumVariableExtensions } from "vellum-ai/api/types/VellumVariableExtensions";

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
    extensions?: VellumVariableExtensions | null;
  };

export declare namespace VellumVariable {
  interface Args {
    variable: VellumVariableWithName;
  }
}

export class VellumVariable extends AstNode {
  private readonly field: python.Field;
  private readonly variable: VellumVariableWithName;

  constructor({ variable }: VellumVariable.Args) {
    super();
    this.variable = variable;
    this.field = python.field({
      name: variable.name ?? variable.key,
      type: getVellumVariablePrimitiveType(variable.type),
      initializer: variable.default
        ? this.generateInitializerIfDefault(variable)
        : undefined,
    });
    this.inheritReferences(this.field);
  }

  private generateInitializerIfDefault(
    variable: VellumVariableWithName
  ): AstNode | undefined {
    return variable.default
      ? new VellumValue({
          vellumValue: variable.default,
        })
      : undefined;
  }

  public write(writer: Writer): void {
    this.field.write(writer);
  }
}
