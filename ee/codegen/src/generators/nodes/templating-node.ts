import { VellumVariableType } from "vellum-ai/api/types";

import { OUTPUTS_CLASS_NAME, VELLUM_CLIENT_MODULE_PATH } from "src/constants";
import { TemplatingNodeContext } from "src/context/node-context/templating-node";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { AstNode } from "src/generators/extensions/ast-node";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { DictInstantiation } from "src/generators/extensions/dict-instantiation";
import { Field } from "src/generators/extensions/field";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { Reference } from "src/generators/extensions/reference";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { TypeReference } from "src/generators/extensions/type-reference";
import { UuidInstantiation } from "src/generators/extensions/uuid-instantiation";
import { BaseNode } from "src/generators/nodes/bases/base";
import { TemplatingNode as TemplatingNodeType } from "src/types/vellum";
import { getVellumVariablePrimitiveType } from "src/utils/vellum-variables";

const TEMPLATING_INPUT_KEY = "template";
const INPUTS_PREFIX = "inputs";

export class TemplatingNode extends BaseNode<
  TemplatingNodeType,
  TemplatingNodeContext
> {
  protected getNodeAttributeNameByNodeInputKey(nodeInputKey: string): string {
    if (nodeInputKey === TEMPLATING_INPUT_KEY) {
      return nodeInputKey;
    }

    return `${INPUTS_PREFIX}.${nodeInputKey}`;
  }

  protected getNodeBaseGenericTypes(): AstNode[] {
    const stateType = this.getStateTypeOrBaseState();
    const primitiveOutputType = this.generateOutputType(
      this.nodeData.data.outputType
    );
    return [stateType, primitiveOutputType];
  }

  protected getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    const otherInputs = Array.from(this.nodeInputsByKey.values()).filter(
      (nodeInput) =>
        nodeInput.nodeInputData.id !== this.nodeData.data.templateNodeInputId
    );

    statements.push(
      new Field({
        name: TEMPLATING_INPUT_KEY,
        initializer: this.getTemplatingInput(),
      })
    );

    statements.push(
      new Field({
        name: INPUTS_PREFIX,
        initializer: new DictInstantiation(
          otherInputs.map((codeInput) => ({
            key: new StrInstantiation(codeInput.nodeInputData.key),
            value: codeInput,
          })),
          {
            endWithComma: true,
          }
        ),
      })
    );

    return statements;
  }

  protected getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    statements.push(
      new Field({
        name: "target_handle_id",
        initializer: new UuidInstantiation(this.nodeData.data.targetHandleId),
      })
    );

    return statements;
  }

  private getTemplatingInput() {
    const templatingInput = this.nodeData.inputs.find(
      (input) => input.id === this.nodeData.data.templateNodeInputId
    );
    if (!templatingInput) {
      this.workflowContext.addError(
        new NodeAttributeGenerationError(
          "Templating input not found",
          "WARNING"
        )
      );
      return new StrInstantiation("");
    }

    const templateRule = templatingInput.value.rules[0];
    if (!templateRule) {
      this.workflowContext.addError(
        new NodeAttributeGenerationError(
          "Templating input rule not found",
          "WARNING"
        )
      );
      return new StrInstantiation("");
    }

    if (templateRule.type !== "CONSTANT_VALUE") {
      this.workflowContext.addError(
        new NodeAttributeGenerationError(
          "Templating input rule is not a constant value",
          "WARNING"
        )
      );
      return new StrInstantiation("");
    }

    if (templateRule.data.type !== "STRING") {
      this.workflowContext.addError(
        new NodeAttributeGenerationError(
          "Templating input rule is not a string",
          "WARNING"
        )
      );
      return new StrInstantiation("");
    }

    if (!templateRule.data.value) {
      this.workflowContext.addError(
        new NodeAttributeGenerationError(
          "Templating input rule value must be defined and nonempty",
          "WARNING"
        )
      );
      return new StrInstantiation("");
    }

    return new StrInstantiation(templateRule.data.value, {
      multiline: true,
      startOnNewLine: true,
      endWithNewLine: true,
    });
  }

  protected getOutputDisplay(): Field {
    return new Field({
      name: "output_display",
      initializer: new DictInstantiation([
        {
          key: new Reference({
            name: this.nodeContext.nodeClassName,
            modulePath: this.nodeContext.nodeModulePath,
            attribute: [OUTPUTS_CLASS_NAME, "result"],
          }),
          value: new ClassInstantiation({
            classReference: new Reference({
              name: "NodeOutputDisplay",
              modulePath:
                this.workflowContext.sdkModulePathNames
                  .NODE_DISPLAY_TYPES_MODULE_PATH,
            }),
            arguments_: [
              new MethodArgument({
                name: "id",
                value: new UuidInstantiation(this.nodeData.data.outputId),
              }),
              new MethodArgument({
                name: "name",
                value: new StrInstantiation("result"),
              }),
            ],
          }),
        },
      ]),
    });
  }

  protected getErrorOutputId(): string | undefined {
    return this.nodeData.data.errorOutputId;
  }

  private generateOutputType(outputType: VellumVariableType): AstNode {
    return outputType === VellumVariableType.Json
      ? new TypeReference(
          new Reference({
            name: "Json",
            modulePath: [
              ...VELLUM_CLIENT_MODULE_PATH,
              "workflows",
              "types",
              "core",
            ],
          })
        )
      : getVellumVariablePrimitiveType(outputType);
  }
}
