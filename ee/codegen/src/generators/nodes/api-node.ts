import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { isNil } from "lodash";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { ApiNodeContext } from "src/context/node-context/api-node";
import { NodeInput } from "src/generators";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { BaseNode } from "src/generators/nodes/bases/base";
import { ApiNode as ApiNodeType, ConstantValuePointer } from "src/types/vellum";

const BODY_INPUT_KEY = "body";
const JSON_ATTRIBUTE_NAME = "json";

export class ApiNode extends BaseNode<ApiNodeType, ApiNodeContext> {
  protected getNodeAttributeNameByNodeInputKey(nodeInputKey: string): string {
    if (nodeInputKey === BODY_INPUT_KEY) {
      // This field was renamed in the SDK for consistency with `requests` pip package
      return JSON_ATTRIBUTE_NAME;
    }

    return nodeInputKey;
  }

  getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    const urlInput = this.nodeInputsByKey.get("url");
    statements.push(
      python.field({
        name: "url",
        initializer: urlInput || python.TypeInstantiation.str(""),
      })
    );

    const methodValue = this.convertMethodValueToEnum();
    if (methodValue.toString() !== "APIRequestMethod.GET") {
      statements.push(
        python.field({
          name: "method",
          initializer: methodValue,
        })
      );
    }
    const body = this.nodeInputsByKey.get("body");
    if (body && body.toString() !== "{}" && body.toString() !== "None") {
      statements.push(
        python.field({
          name: "json",
          initializer: body,
        })
      );
    }

    const additionalHeaders = this.nodeData.data.additionalHeaders;
    if (additionalHeaders && additionalHeaders.length > 0) {
      statements.push(
        python.field({
          name: "headers",
          initializer: python.TypeInstantiation.dict(
            additionalHeaders.map((header) => {
              const keyInput = this.nodeData.inputs.find(
                (input) => input.id === header.headerKeyInputId
              );
              const valueInput = this.nodeData.inputs.find(
                (input) => input.id === header.headerValueInputId
              );

              if (!keyInput || !valueInput) {
                throw new NodeAttributeGenerationError(
                  `Input not found for header: ${JSON.stringify(header)}`
                );
              }
              const key = new NodeInput({
                nodeContext: this.nodeContext,
                nodeInputData: keyInput,
              });
              const value = new NodeInput({
                nodeContext: this.nodeContext,
                nodeInputData: valueInput,
              });

              return {
                key,
                value,
              };
            }),
            {
              endWithComma: true,
            }
          ),
        })
      );
    }

    const apiKeyHeaderKeyInput = this.nodeData.data.apiKeyHeaderKeyInputId;
    if (apiKeyHeaderKeyInput) {
      const keyInput = this.nodeData.inputs.find(
        (input) => input.id === apiKeyHeaderKeyInput
      );
      if (!keyInput) {
        throw new NodeAttributeGenerationError(
          `No inputs have api header key id of ${apiKeyHeaderKeyInput}`
        );
      }
      const key = this.nodeInputsByKey.get(keyInput.key);
      if (!key) {
        throw new NodeAttributeGenerationError(
          `No inputs have key of ${keyInput.key}`
        );
      }
      statements.push(
        python.field({
          name: "api_key_header_key",
          initializer: key,
        })
      );
    }

    const authTypeEnum = this.convertAuthTypeValueToEnum();
    if (authTypeEnum) {
      statements.push(
        python.field({
          name: "authorization_type",
          initializer: authTypeEnum,
        })
      );
      if (this.nodeData.data.apiKeyHeaderValueInputId) {
        const valueInput = this.nodeData.inputs.find(
          (input) => input.id === this.nodeData.data.apiKeyHeaderValueInputId
        );
        if (!valueInput) {
          throw new NodeAttributeGenerationError(
            `No inputs have api header value id of ${this.nodeData.data.apiKeyHeaderValueInputId}`
          );
        }
        const value = this.nodeInputsByKey.get(valueInput.key);
        if (!value) {
          throw new NodeAttributeGenerationError(
            `No inputs have key of ${valueInput.key}`
          );
        }
        statements.push(
          python.field({
            name: "api_key_header_value",
            initializer: value,
          })
        );
      }

      if (this.nodeData.data.bearerTokenValueInputId) {
        const valueInput = this.nodeData.inputs.find(
          (input) => input.id === this.nodeData.data.bearerTokenValueInputId
        );
        if (!valueInput) {
          throw new NodeAttributeGenerationError(
            `No inputs have bearer token header value id of ${this.nodeData.data.bearerTokenValueInputId}`
          );
        }
        const value = this.nodeInputsByKey.get(valueInput.key);
        if (!value) {
          throw new NodeAttributeGenerationError(
            `No inputs have key of ${valueInput.key}`
          );
        }
        statements.push(
          python.field({
            name: "bearer_token_value",
            initializer: value,
          })
        );
      }
    }

    return statements;
  }

  getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    statements.push(
      python.field({
        name: "label",
        initializer: python.TypeInstantiation.str(this.nodeData.data.label),
      })
    );

    statements.push(
      python.field({
        name: "node_id",
        initializer: python.TypeInstantiation.uuid(this.nodeData.id),
      })
    );

    statements.push(
      python.field({
        name: "target_handle_id",
        initializer: python.TypeInstantiation.uuid(
          this.nodeData.data.targetHandleId
        ),
      })
    );

    if (!isNil(this.nodeData.data.additionalHeaders)) {
      statements.push(
        python.field({
          name: "additional_header_key_input_ids",
          initializer: python.TypeInstantiation.dict(
            this.nodeData.data.additionalHeaders.map((header) => {
              const nodeInput = this.nodeData.inputs.find(
                (nodeInput) => nodeInput.id === header.headerKeyInputId
              );

              if (!nodeInput) {
                throw new NodeAttributeGenerationError(
                  `Node input with ID ${header.headerKeyInputId} not found`
                );
              }
              const key = new NodeInput({
                nodeContext: this.nodeContext,
                nodeInputData: nodeInput,
              });

              return {
                key,
                value: python.TypeInstantiation.uuid(nodeInput.id),
              };
            })
          ),
        })
      );
    }

    if (!isNil(this.nodeData.data.additionalHeaders)) {
      statements.push(
        python.field({
          name: "additional_header_value_input_ids",
          initializer: python.TypeInstantiation.dict(
            this.nodeData.data.additionalHeaders.map((header) => {
              const nodeInput = this.nodeData.inputs.find(
                (nodeInput) => nodeInput.id === header.headerKeyInputId
              );

              if (!nodeInput) {
                throw new NodeAttributeGenerationError(
                  `Node input with ID ${header.headerKeyInputId} not found`
                );
              }
              const key = new NodeInput({
                nodeContext: this.nodeContext,
                nodeInputData: nodeInput,
              });

              return {
                key,
                value: python.TypeInstantiation.uuid(header.headerValueInputId),
              };
            })
          ),
        })
      );
    }

    return statements;
  }

  protected getOutputDisplay(): python.Field {
    return python.field({
      name: "output_display",
      initializer: python.TypeInstantiation.dict([
        {
          key: python.reference({
            name: this.nodeContext.nodeClassName,
            modulePath: this.nodeContext.nodeModulePath,
            attribute: [OUTPUTS_CLASS_NAME, "json"],
          }),
          value: python.instantiateClass({
            classReference: python.reference({
              name: "NodeOutputDisplay",
              modulePath:
                this.workflowContext.sdkModulePathNames
                  .NODE_DISPLAY_TYPES_MODULE_PATH,
            }),
            arguments_: [
              python.methodArgument({
                name: "id",
                value: python.TypeInstantiation.uuid(
                  this.nodeData.data.jsonOutputId
                ),
              }),
              python.methodArgument({
                name: "name",
                value: python.TypeInstantiation.str("json"),
              }),
            ],
          }),
        },
        {
          key: python.reference({
            name: this.nodeContext.nodeClassName,
            modulePath: this.nodeContext.nodeModulePath,
            attribute: [OUTPUTS_CLASS_NAME, "status_code"],
          }),
          value: python.instantiateClass({
            classReference: python.reference({
              name: "NodeOutputDisplay",
              modulePath:
                this.workflowContext.sdkModulePathNames
                  .NODE_DISPLAY_TYPES_MODULE_PATH,
            }),
            arguments_: [
              python.methodArgument({
                name: "id",
                value: python.TypeInstantiation.uuid(
                  this.nodeData.data.statusCodeOutputId
                ),
              }),
              python.methodArgument({
                name: "name",
                value: python.TypeInstantiation.str("status_code"),
              }),
            ],
          }),
        },
        {
          key: python.reference({
            name: this.nodeContext.nodeClassName,
            modulePath: this.nodeContext.nodeModulePath,
            attribute: [OUTPUTS_CLASS_NAME, "text"],
          }),
          value: python.instantiateClass({
            classReference: python.reference({
              name: "NodeOutputDisplay",
              modulePath:
                this.workflowContext.sdkModulePathNames
                  .NODE_DISPLAY_TYPES_MODULE_PATH,
            }),
            arguments_: [
              python.methodArgument({
                name: "id",
                value: python.TypeInstantiation.uuid(
                  this.nodeData.data.textOutputId
                ),
              }),
              python.methodArgument({
                name: "name",
                value: python.TypeInstantiation.str("text"),
              }),
            ],
          }),
        },
      ]),
    });
  }

  getErrorOutputId(): string | undefined {
    return this.nodeData.data.errorOutputId;
  }

  private convertMethodValueToEnum(): AstNode {
    const methodValue = this.nodeData.inputs
      .find((input) => input.id === this.nodeData.data.methodInputId)
      ?.value.rules.find(
        (value) => value.type === "CONSTANT_VALUE"
      ) as ConstantValuePointer;

    if (!methodValue) {
      throw new NodeAttributeGenerationError(
        `No method input found for input id ${this.nodeData.data.methodInputId} and of type "CONSTANT_VALUE"`
      );
    }
    const methodEnum = methodValue.data.value as string;

    return python.reference({
      name: "APIRequestMethod",
      modulePath: [
        ...this.workflowContext.sdkModulePathNames.WORKFLOWS_MODULE_PATH,
        "constants",
      ],
      attribute: [methodEnum],
    });
  }

  private convertAuthTypeValueToEnum(): AstNode | undefined {
    if (isNil(this.nodeData.data.authorizationTypeInputId)) {
      return undefined;
    }

    const authValue = this.nodeData.inputs
      .find((input) => input.id === this.nodeData.data.authorizationTypeInputId)
      ?.value.rules.find(
        (value) => value.type === "CONSTANT_VALUE"
      ) as ConstantValuePointer;

    if (!authValue) {
      throw new NodeAttributeGenerationError(
        `No auth type input found for input id ${this.nodeData.data.authorizationTypeInputId} and of type "CONSTANT_VALUE"`
      );
    }

    const authTypeEnum = authValue.data.value as string;

    if (!authTypeEnum) {
      return undefined;
    } else {
      return python.reference({
        name: "AuthorizationType",
        modulePath: [
          ...this.workflowContext.sdkModulePathNames.WORKFLOWS_MODULE_PATH,
          "constants",
        ],
        attribute: [authTypeEnum],
      });
    }
  }
}
