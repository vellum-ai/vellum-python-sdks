import { python } from "@fern-api/python-ast";
import { ClassInstantiation } from "@fern-api/python-ast/ClassInstantiation";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import {
  OUTPUTS_CLASS_NAME,
  VELLUM_CLIENT_MODULE_PATH,
  VELLUM_WORKFLOW_NODE_BASE_TYPES_PATH,
} from "src/constants";
import { TextSearchNodeContext } from "src/context/node-context/text-search-node";
import { NodeInput } from "src/generators";
import {
  NodeAttributeGenerationError,
  ValueGenerationError,
} from "src/generators/errors";
import { BaseNode } from "src/generators/nodes/bases/base";
import { VellumValueLogicalExpressionSerializer } from "src/serializers/vellum";
import {
  ConstantValuePointer,
  SearchNode as SearchNodeType,
  VellumLogicalConditionGroup as VellumLogicalConditionGroupType,
  VellumLogicalCondition as VellumLogicalConditionType,
  VellumLogicalExpression,
  VellumLogicalExpression as VellumLogicalExpressionType,
} from "src/types/vellum";
import { isUnaryOperator } from "src/utils/nodes";

export class SearchNode extends BaseNode<
  SearchNodeType,
  TextSearchNodeContext
> {
  getNodeClassBodyStatements(): AstNode[] {
    const bodyStatements: AstNode[] = [];

    const query = this.getNodeInputByName("query");
    if (query) {
      bodyStatements.push(
        python.field({
          name: "query",
          initializer: query,
        })
      );
    }

    const documentName = this.nodeContext.documentIndex?.name;
    const documentIndex = this.getNodeInputByName("document_index_id");
    bodyStatements.push(
      python.field({
        name: "document_index",
        initializer: documentName
          ? python.TypeInstantiation.str(documentName)
          : documentIndex ?? python.TypeInstantiation.none(),
      })
    );

    const limitInput = this.findNodeInputByName("limit");
    if (limitInput) {
      const limitValue = limitInput.nodeInputData?.value.rules[0];
      if (
        limitValue?.type === "CONSTANT_VALUE" &&
        limitValue.data.type === "STRING"
      ) {
        if (limitValue.data.value != null) {
          const parsedInt = parseInt(limitValue.data.value);
          if (isNaN(parsedInt)) {
            throw new ValueGenerationError(
              `Failed to parse search node limit value "${limitValue.data.value}" as an integer`
            );
          }
          bodyStatements.push(
            python.field({
              name: "limit",
              initializer: python.TypeInstantiation.int(parsedInt),
            })
          );
        }
      } else if (
        limitValue?.type === "CONSTANT_VALUE" &&
        limitValue.data.type !== "NUMBER"
      ) {
        throw new NodeAttributeGenerationError(
          `Limit param input should be a CONSTANT_VALUE and of type NUMBER, got ${limitValue.data.type} instead`
        );
      } else {
        bodyStatements.push(
          python.field({
            name: "limit",
            initializer: limitInput,
          })
        );
      }
    }

    bodyStatements.push(
      python.field({
        name: "weights",
        initializer: this.getSearchWeightsRequest(),
      })
    );

    bodyStatements.push(
      python.field({
        name: "result_merging",
        initializer: this.getResultMerging(),
      })
    );

    bodyStatements.push(
      python.field({
        name: "filters",
        initializer: this.searchFiltersConfig(),
      })
    );

    const separator = this.findNodeInputByName("separator");

    if (separator) {
      bodyStatements.push(
        python.field({
          name: "chunk_separator",
          initializer: separator,
        })
      );
    }
    return bodyStatements;
  }

  private getSearchWeightsRequest(): ClassInstantiation {
    const weightsRule =
      this.findNodeInputByName("weights")?.nodeInputData?.value.rules[0];
    if (!weightsRule || weightsRule.type !== "CONSTANT_VALUE") {
      throw new NodeAttributeGenerationError("weights input is required");
    }

    // TODO: Determine what we want to cast JSON values to
    //  https://app.shortcut.com/vellum/story/5459
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const { semantic_similarity, keywords } = weightsRule.data.value as Record<
      string,
      unknown
    >;
    if (typeof semantic_similarity !== "number") {
      throw new NodeAttributeGenerationError(
        "semantic_similarity weight must be a number"
      );
    }

    if (typeof keywords !== "number") {
      throw new NodeAttributeGenerationError(
        "keywords weight must be a number"
      );
    }

    const searchWeightsRequest = python.instantiateClass({
      classReference: python.reference({
        name: "SearchWeightsRequest",
        modulePath: VELLUM_CLIENT_MODULE_PATH,
      }),
      arguments_: [
        python.methodArgument({
          name: "semantic_similarity",
          value: python.TypeInstantiation.float(semantic_similarity),
        }),
        python.methodArgument({
          name: "keywords",
          value: python.TypeInstantiation.float(keywords),
        }),
      ],
    });

    return searchWeightsRequest;
  }

  private getResultMerging(): ClassInstantiation {
    const resultMergingRule = this.findNodeInputByName("result_merging_enabled")
      ?.nodeInputData?.value.rules[0];
    if (!resultMergingRule || resultMergingRule.type !== "CONSTANT_VALUE") {
      throw new NodeAttributeGenerationError(
        "result_merging_enabled input is required"
      );
    }

    const resultMergingEnabled = resultMergingRule.data.value;
    if (typeof resultMergingEnabled !== "string") {
      throw new NodeAttributeGenerationError(
        "result_merging_enabled must be a boolean"
      );
    }

    return python.instantiateClass({
      classReference: python.reference({
        name: "SearchResultMergingRequest",
        modulePath: VELLUM_CLIENT_MODULE_PATH,
      }),
      arguments_: [
        python.methodArgument({
          name: "enabled",
          value: python.TypeInstantiation.bool(Boolean(resultMergingEnabled)),
        }),
      ],
    });
  }

  private searchFiltersConfig(): ClassInstantiation {
    let rawMetadata;
    const metadataNodeInput = this.nodeInputsByKey.get("metadata_filters");
    if (metadataNodeInput) {
      rawMetadata = this.convertNodeInputToMetadata(metadataNodeInput);
    }

    return python.instantiateClass({
      classReference: python.reference({
        name: "SearchFilters",
        modulePath: VELLUM_WORKFLOW_NODE_BASE_TYPES_PATH,
      }),
      arguments_: [
        python.methodArgument({
          name: "external_ids",
          value:
            this.findNodeInputByName("external_id_filters") ??
            python.TypeInstantiation.none(),
        }),
        python.methodArgument({
          name: "metadata",
          value: rawMetadata
            ? new SearchNodeMetadataFilters({
                metadata: rawMetadata,
                nodeInputsById: this.nodeInputsById,
              })
            : python.TypeInstantiation.none(),
        }),
      ],
    });
  }

  private convertNodeInputToMetadata(
    nodeInput: NodeInput
  ): VellumLogicalExpression | undefined {
    const rules = nodeInput.nodeInputData.value.rules;

    const nodeInputValuePointer = rules.find(
      (rule): rule is ConstantValuePointer =>
        rule.type === "CONSTANT_VALUE" && rule.data.type === "JSON"
    );

    if (!nodeInputValuePointer) {
      return;
    }

    const metadataFilters = nodeInputValuePointer.data.value;
    if (!metadataFilters) {
      return undefined;
    }

    const parsedData =
      VellumValueLogicalExpressionSerializer.parse(metadataFilters);

    if (!parsedData.ok) {
      throw new NodeAttributeGenerationError(
        `Failed to parse metadata filter JSON: ${JSON.stringify(
          parsedData.errors
        )}`
      );
    }

    return parsedData.value;
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

    let rawMetadata;
    const metadataNodeInput = this.nodeInputsByKey.get("metadata_filters");
    if (metadataNodeInput) {
      rawMetadata = this.convertNodeInputToMetadata(metadataNodeInput);
      if (rawMetadata) {
        const metadataFilterInputIdByOperandId =
          this.generateMetadataFilterInputIdByOperandIdMap(rawMetadata);

        statements.push(
          python.field({
            name: "metadata_filter_input_id_by_operand_id",
            initializer: python.TypeInstantiation.dict(
              Array.from(metadataFilterInputIdByOperandId.entries()).map(
                ([metadataFilterOperandId, metadataFilterNodeInputId]) => {
                  return {
                    key: python.TypeInstantiation.uuid(metadataFilterOperandId),
                    value: python.TypeInstantiation.uuid(
                      metadataFilterNodeInputId
                    ),
                  };
                }
              )
            ),
          })
        );
      }
    }

    return statements;
  }

  private generateMetadataFilterInputIdByOperandIdMap(
    rawData: VellumLogicalExpression
  ): Map<string, string> {
    const result = new Map<string, string>();

    const traverse = (
      logicalExpression: VellumLogicalExpression,
      conditionPath: number[]
    ) => {
      if (logicalExpression.type === "LOGICAL_CONDITION") {
        const lhsQueryInput = this.nodeInputsById.get(
          logicalExpression.lhsVariableId
        )?.nodeInputData?.id;
        const rhsQueryInput = this.nodeInputsById.get(
          logicalExpression.rhsVariableId
        )?.nodeInputData?.id;
        if (!lhsQueryInput) {
          this.workflowContext.addError(
            new NodeAttributeGenerationError(
              `Could not find search node query input for the left hand side of condition ${conditionPath.join(
                " -> "
              )}`,
              "WARNING"
            )
          );
          return;
        }
        if (!isUnaryOperator(logicalExpression.operator) && !rhsQueryInput) {
          this.workflowContext.addError(
            new NodeAttributeGenerationError(
              `Could not find search node query input for the right hand side of condition ${conditionPath.join(
                " -> "
              )}`,
              "WARNING"
            )
          );
          return;
        }

        result.set(logicalExpression.lhsVariableId, lhsQueryInput);

        if (rhsQueryInput) {
          result.set(logicalExpression.rhsVariableId, rhsQueryInput);
        }
      } else if (logicalExpression.type === "LOGICAL_CONDITION_GROUP") {
        logicalExpression.conditions.forEach((condition, index) =>
          traverse(condition, [...conditionPath, index])
        );
      }
    };

    traverse(rawData, []);

    return result;
  }

  protected getOutputDisplay(): python.Field {
    return python.field({
      name: "output_display",
      initializer: python.TypeInstantiation.dict([
        {
          key: python.reference({
            name: this.nodeContext.nodeClassName,
            modulePath: this.nodeContext.nodeModulePath,
            attribute: [OUTPUTS_CLASS_NAME, "results"],
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
                  this.nodeData.data.resultsOutputId
                ),
              }),
              python.methodArgument({
                name: "name",
                value: python.TypeInstantiation.str("results"),
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

  protected getErrorOutputId(): string | undefined {
    return this.nodeData.data.errorOutputId;
  }
}

export declare namespace SearchNodeMetadataFilters {
  export interface Args {
    metadata: VellumLogicalExpressionType;
    nodeInputsById: Map<string, NodeInput>;
  }
}

export class SearchNodeMetadataFilters extends AstNode {
  private metadata: VellumLogicalExpressionType;
  private nodeInputsById: Map<string, NodeInput>;
  private astNode: AstNode;

  public constructor(args: SearchNodeMetadataFilters.Args) {
    super();

    this.metadata = args.metadata;
    this.nodeInputsById = args.nodeInputsById;
    this.astNode = this.generateAstNode();
    this.inheritReferences(this.astNode);
  }

  private generateAstNode(): AstNode {
    switch (this.metadata.type) {
      case "LOGICAL_CONDITION":
        return this.generateLogicalConditionArguments(this.metadata);
      case "LOGICAL_CONDITION_GROUP":
        return this.generateLogicalConditionGroupArguments(this.metadata);
    }
  }

  private generateLogicalConditionGroupArguments(
    data: VellumLogicalConditionGroupType
  ): python.ClassInstantiation {
    const processCondition = (
      condition: VellumLogicalExpressionType
    ): AstNode => {
      if (condition.type === "LOGICAL_CONDITION") {
        return this.generateLogicalConditionArguments(condition);
      } else {
        return this.generateLogicalConditionGroupArguments(condition);
      }
    };

    const processedConditions: AstNode[] = data.conditions.map((condition) =>
      processCondition(condition)
    );

    return python.instantiateClass({
      classReference: python.reference({
        name: "MetadataLogicalConditionGroup",
        modulePath: VELLUM_WORKFLOW_NODE_BASE_TYPES_PATH,
      }),
      arguments_: [
        python.methodArgument({
          name: "combinator",
          value: python.TypeInstantiation.str(data.combinator),
        }),
        python.methodArgument({
          name: "negated",
          value: python.TypeInstantiation.bool(data.negated),
        }),
        python.methodArgument({
          name: "conditions",
          value: python.TypeInstantiation.list(processedConditions),
        }),
      ],
    });
  }

  private generateLogicalConditionArguments(
    data: VellumLogicalConditionType
  ): python.ClassInstantiation {
    const args: python.MethodArgument[] = [];

    const lhsId = data.lhsVariableId;
    const lhs = this.nodeInputsById.get(lhsId);
    if (!lhs) {
      throw new NodeAttributeGenerationError(
        `Could not find search node input for id ${lhsId}`
      );
    }

    args.push(
      python.methodArgument({
        name: "lhs_variable",
        value: lhs,
      }),
      python.methodArgument({
        name: "operator",
        value: python.TypeInstantiation.str(data.operator),
      })
    );

    const rhsId = data.rhsVariableId;
    const rhs = this.nodeInputsById.get(rhsId);
    if (!isUnaryOperator(data.operator) && !rhs) {
      throw new NodeAttributeGenerationError(
        `Could not find search node input for id ${rhsId}`
      );
    }

    if (rhs) {
      args.push(
        python.methodArgument({
          name: "rhs_variable",
          value: rhs,
        })
      );
    }

    return python.instantiateClass({
      classReference: python.reference({
        name: "MetadataLogicalCondition",
        modulePath: VELLUM_WORKFLOW_NODE_BASE_TYPES_PATH,
      }),
      arguments_: args,
    });
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}
