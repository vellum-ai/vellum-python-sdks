import { python } from "@fern-api/python-ast";
import { ClassInstantiation } from "@fern-api/python-ast/ClassInstantiation";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { OUTPUTS_CLASS_NAME, VELLUM_CLIENT_MODULE_PATH } from "src/constants";
import { TextSearchNodeContext } from "src/context/node-context/text-search-node";
import { NodeInput } from "src/generators";
import { BaseSingleFileNode } from "src/generators/nodes/bases/single-file-base";
import { VellumValueLogicalExpressionSerializer } from "src/serializers/vellum";
import {
  ConstantValuePointer,
  SearchNode as SearchNodeType,
  VellumLogicalCondition as VellumLogicalConditionType,
  VellumLogicalConditionGroup as VellumLogicalConditionGroupType,
  VellumLogicalExpression as VellumLogicalExpressionType,
  VellumLogicalExpression,
} from "src/types/vellum";

export class SearchNode extends BaseSingleFileNode<
  SearchNodeType,
  TextSearchNodeContext
> {
  getNodeClassBodyStatements(): AstNode[] {
    const bodyStatements: AstNode[] = [];

    bodyStatements.push(
      python.field({
        name: "query",
        initializer: this.getNodeInputByName("query"),
      })
    );

    bodyStatements.push(
      python.field({
        name: "document_index",
        initializer: this.getNodeInputByName("document_index_id"),
      })
    );

    const options = python.instantiateClass({
      classReference: python.reference({
        name: "SearchRequestOptionsRequest",
        modulePath: VELLUM_CLIENT_MODULE_PATH,
      }),
      arguments_: [
        python.methodArgument({
          name: "limit",
          value:
            this.findNodeInputByName("limit") ??
            python.TypeInstantiation.none(),
        }),
        python.methodArgument({
          name: "weights",
          value: this.getSearchWeightsRequest(),
        }),
        python.methodArgument({
          name: "result_merging",
          value: this.getResultMerging(),
        }),
        python.methodArgument({
          name: "filters",
          value: this.searchFiltersConfig(),
        }),
      ],
    });

    bodyStatements.push(
      python.field({
        name: "options",
        initializer: options,
      })
    );

    bodyStatements.push(
      python.field({
        name: "chunk_separator",
        initializer: this.getNodeInputByName("separator"),
      })
    );

    return bodyStatements;
  }

  private getSearchWeightsRequest(): ClassInstantiation {
    const weightsRule =
      this.findNodeInputByName("weights")?.nodeInputData?.value.rules[0];
    if (!weightsRule || weightsRule.type !== "CONSTANT_VALUE") {
      throw new Error("weights input is required");
    }

    // TODO: Determine what we want to cast JSON values to
    //  https://app.shortcut.com/vellum/story/5459
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const { semantic_similarity, keywords } = weightsRule.data.value as Record<
      string,
      unknown
    >;
    if (typeof semantic_similarity !== "number") {
      throw new Error("semantic_similarity weight must be a number");
    }

    if (typeof keywords !== "number") {
      throw new Error("keywords weight must be a number");
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
      throw new Error("result_merging_enabled input is required");
    }

    const resultMergingEnabled = resultMergingRule.data.value;
    if (typeof resultMergingEnabled !== "string") {
      throw new Error("result_merging_enabled must be a boolean");
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
        name: "SearchFiltersRequest",
        modulePath: VELLUM_CLIENT_MODULE_PATH,
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
      throw new Error(
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
    const prefix = "vellum-query-builder-variable-";

    const traverse = (logicalExpression: VellumLogicalExpression) => {
      if (logicalExpression.type === "LOGICAL_CONDITION") {
        const lhsQueryInput = this.nodeInputsById.get(
          logicalExpression.lhsVariableId
        )?.nodeInputData?.id;
        const rhsQueryInput = this.nodeInputsById.get(
          logicalExpression.rhsVariableId
        )?.nodeInputData?.id;
        if (!lhsQueryInput) {
          throw new Error(
            `Could not find node input for id ${logicalExpression.lhsVariableId}`
          );
        }
        if (!rhsQueryInput) {
          throw new Error(
            `Could not find node input for id ${logicalExpression.rhsVariableId}`
          );
        }

        result.set(logicalExpression.lhsVariableId, rhsQueryInput);
        result.set(logicalExpression.rhsVariableId, rhsQueryInput);
      } else if (logicalExpression.type === "LOGICAL_CONDITION_GROUP") {
        logicalExpression.conditions.forEach((condition) =>
          traverse(condition)
        );
      }
    };

    traverse(rawData);

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
        name: "VellumValueLogicalConditionGroupRequest",
        modulePath: [...VELLUM_CLIENT_MODULE_PATH, "types"],
      }),
      arguments_: [
        python.methodArgument({
          name: "type",
          value: python.TypeInstantiation.str("LOGICAL_CONDITION_GROUP"),
        }),
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
    const lhsId = data.lhsVariableId;
    const lhs = this.nodeInputsById.get(lhsId);
    if (!lhs) {
      throw new Error(`Could not find node input for id ${lhsId}`);
    }

    const rhsId = data.rhsVariableId;
    const rhs = this.nodeInputsById.get(rhsId);
    if (!rhs) {
      throw new Error(`Could not find node input for id ${rhsId}`);
    }

    return python.instantiateClass({
      classReference: python.reference({
        name: "VellumValueLogicalConditionRequest",
        modulePath: [...VELLUM_CLIENT_MODULE_PATH, "types"],
      }),
      arguments_: [
        python.methodArgument({
          name: "type",
          value: python.TypeInstantiation.str("LOGICAL_CONDITION"),
        }),
        python.methodArgument({
          name: "lhs_variable",
          value: lhs,
        }),
        python.methodArgument({
          name: "operator",
          value: python.TypeInstantiation.str(data.operator),
        }),
        python.methodArgument({
          name: "rhs_variable",
          value: rhs,
        }),
      ],
    });
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}
