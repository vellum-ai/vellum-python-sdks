import { python } from "@fern-api/python-ast";
import { Reference } from "@fern-api/python-ast/Reference";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { PORTS_CLASS_NAME } from "src/constants";
import { ConditionalNodeContext } from "src/context/node-context/conditional-node";
import { ConditionalNodePort } from "src/generators/conditional-node-port";
import { BaseSingleFileNode } from "src/generators/nodes/bases/single-file-base";
import {
  ConditionalNode as ConditionalNodeType,
  ConditionalNodeData,
  ConditionalRuleData,
  NodeInput,
  NodeInputValuePointer,
} from "src/types/vellum";

export class ConditionalNode extends BaseSingleFileNode<
  ConditionalNodeType,
  ConditionalNodeContext
> {
  baseNodeClassName = "ConditionalNode";
  baseNodeDisplayClassName = "BaseConditionalNodeDisplay";

  protected getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    const inputFieldsByRuleId = new Map<string, NodeInput>();
    const valueInputsByRuleId = new Map<string, NodeInputValuePointer>();
    this.constructMapContextForAllConditions(
      inputFieldsByRuleId,
      valueInputsByRuleId,
      this.nodeData.data
    );

    const baseNodeClassRef = this.getNodeBaseClass();

    const ref = python.reference({
      name: baseNodeClassRef.name,
      modulePath: baseNodeClassRef.modulePath,
      alias: baseNodeClassRef.alias,
      attribute: ["Ports"],
    });

    this.getNodeBaseClass().inheritReferences(ref);

    const portsClass = python.class_({
      name: "Ports",
      extends_: [ref],
    });
    Array.from(this.workflowContext.portContextById.entries()).forEach(
      ([portId, context], idx) => {
        const conditionData = this.nodeData.data.conditions.find(
          (condition) => condition.sourceHandleId === portId
        );

        if (!conditionData) {
          return;
        }

        const portName = `branch_${idx + 1}`;

        portsClass.addField(
          python.field({
            name: portName,
            initializer: new ConditionalNodePort({
              portContext: context,
              inputFieldsByRuleId: inputFieldsByRuleId,
              valueInputsByRuleIds: valueInputsByRuleId,
              conditionData: conditionData,
            }),
          })
        );
      }
    );

    statements.push(portsClass);
    return statements;
  }

  protected getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    statements.push(
      python.field({
        name: "label",
        initializer: python.TypeInstantiation.str(this.nodeData.data.label),
      }),
      python.field({
        name: "node_id",
        initializer: python.TypeInstantiation.uuid(this.nodeData.id),
      }),
      python.field({
        name: "target_handle_id",
        initializer: python.TypeInstantiation.uuid(
          this.nodeData.data.targetHandleId
        ),
      })
    );

    statements.push(
      python.field({
        name: "source_handle_ids",
        initializer: python.TypeInstantiation.dict(
          this.nodeData.data.conditions.map((condition, idx) => ({
            key: python.TypeInstantiation.int(idx),
            value: python.TypeInstantiation.uuid(condition.sourceHandleId),
          }))
        ),
      })
    );

    const ruleIdMapRef = python.reference({
      name: "RuleIdMap",
      modulePath: [
        ...this.workflowContext.sdkModulePathNames.NODE_DISPLAY_MODULE_PATH,
        "vellum",
        "conditional_node",
      ],
    });

    this.getNodeDisplayBaseClass().inheritReferences(ruleIdMapRef);

    statements.push(
      python.field({
        name: "rule_ids",
        initializer: python.TypeInstantiation.list(
          this.createRuleIdMapList(this.nodeData.data, ruleIdMapRef)
        ),
      })
    );

    const conditionIdRef = python.reference({
      name: "ConditionId",
      modulePath: [
        ...this.workflowContext.sdkModulePathNames.NODE_DISPLAY_MODULE_PATH,
        "vellum",
        "conditional_node",
      ],
    });

    this.getNodeDisplayBaseClass().inheritReferences(conditionIdRef);

    statements.push(
      python.field({
        name: "condition_ids",
        initializer: python.TypeInstantiation.list(
          this.createConditionIdList(this.nodeData.data, conditionIdRef)
        ),
      })
    );

    return statements;
  }

  private createConditionIdList(
    nodeData: ConditionalNodeData,
    conditionIdRef: Reference
  ): AstNode[] {
    const conditionIdsList: AstNode[] = [];
    nodeData.conditions.forEach((condition) => {
      conditionIdsList.push(
        python.instantiateClass({
          classReference: conditionIdRef,
          arguments_: [
            python.methodArgument({
              name: "id",
              value: python.TypeInstantiation.uuid(condition.id),
            }),
            python.methodArgument({
              name: "rule_group_id",
              value: condition.data
                ? python.TypeInstantiation.uuid(condition.data.id)
                : python.TypeInstantiation.none(),
            }),
          ],
        })
      );
    });
    return conditionIdsList;
  }

  private createRuleIdMapList(
    nodeData: ConditionalNodeData,
    ruleIdMapRef: Reference
  ): AstNode[] {
    const ruleIdsList: AstNode[] = [];
    nodeData.conditions.forEach((condition) => {
      if (condition.data) {
        const ruleIdMap = this.createRuleIdMap(condition.data, ruleIdMapRef);
        if (ruleIdMap) {
          ruleIdsList.push(ruleIdMap);
        }
      }
    });

    return ruleIdsList;
  }

  private createRuleIdMap(
    ruleData: ConditionalRuleData,
    ruleIdMapRef: Reference
  ): AstNode | null {
    if (!ruleData) {
      return null;
    }

    let lhs = null;
    let rhs = null;
    let fieldId = null;
    let valueId = null;

    if (!ruleData.rules) {
      fieldId = ruleData.fieldNodeInputId;
      valueId = ruleData.valueNodeInputId;
    }

    // Check first rule in the arr (lhs)
    if (ruleData.rules && ruleData.rules[0]) {
      lhs = this.createRuleIdMap(ruleData.rules[0], ruleIdMapRef);
    }

    // Check second rule in the arr (rhs)
    if (ruleData.rules && ruleData.rules[1]) {
      rhs = this.createRuleIdMap(ruleData.rules[1], ruleIdMapRef);
    }

    return python.instantiateClass({
      classReference: ruleIdMapRef,
      arguments_: [
        python.methodArgument({
          name: "id",
          value: python.TypeInstantiation.uuid(ruleData.id),
        }),
        python.methodArgument({
          name: "lhs",
          value: lhs ? lhs : python.TypeInstantiation.none(),
        }),
        python.methodArgument({
          name: "rhs",
          value: rhs ? rhs : python.TypeInstantiation.none(),
        }),
        python.methodArgument({
          name: "field_node_input_id",
          value: fieldId
            ? python.TypeInstantiation.uuid(fieldId)
            : python.TypeInstantiation.none(),
        }),
        python.methodArgument({
          name: "value_node_input_id",
          value: valueId
            ? python.TypeInstantiation.uuid(valueId)
            : python.TypeInstantiation.none(),
        }),
      ],
    });
  }

  private constructMapContextForAllConditions(
    inputFieldsByRuleId: Map<string, NodeInput>,
    valueInputsByRuleIds: Map<string, unknown>,
    nodeData: ConditionalNodeData
  ): void {
    nodeData.conditions.forEach((condition) => {
      if (condition.data) {
        this.constructMapContextByRuleIds(
          inputFieldsByRuleId,
          valueInputsByRuleIds,
          condition.data
        );
      }
    });
  }

  private constructMapContextByRuleIds(
    inputFieldsByRuleId: Map<string, NodeInput>,
    valueInputsByRuleIds: Map<string, unknown>,
    ruleData: ConditionalRuleData
  ): void {
    const processLeafRule = (rule: ConditionalRuleData): void => {
      if (!rule.id) return;

      if (rule.fieldNodeInputId && !inputFieldsByRuleId.has(rule.id)) {
        processFieldInputs(rule);
      }

      if (rule.valueNodeInputId) {
        processValueNodeInput(rule);
      }
    };

    const processFieldInputs = (rule: ConditionalRuleData): void => {
      this.nodeData.inputs.forEach((input) => {
        if (input.id === rule.fieldNodeInputId) {
          if (!inputFieldsByRuleId.has(rule.id) && input) {
            inputFieldsByRuleId.set(rule.id, input);
          }
        }
      });
    };

    const processValueNodeInput = (rule: ConditionalRuleData): void => {
      this.nodeData.inputs.forEach((input) => {
        if (input.id === rule.valueNodeInputId) {
          input.value.rules.forEach((valuePointer) => {
            let value;
            switch (valuePointer.type) {
              case "CONSTANT_VALUE":
                value = input.value;
                break;
              case "NODE_OUTPUT": {
                value = input.value;
                break;
              }
              case "WORKSPACE_SECRET": {
                value = input.value;
                break;
              }
              case "INPUT_VARIABLE": {
                value = input.value;
                break;
              }
              case "EXECUTION_COUNTER": {
                value = input.value;
                break;
              }
            }
            if (!valueInputsByRuleIds.has(rule.id)) {
              valueInputsByRuleIds.set(rule.id, value);
            }
          });
        }
      });
    };

    const processRule = (rule: ConditionalRuleData): void => {
      if (!rule) return;
      else if (rule.rules && rule.rules.length !== 0) {
        rule.rules.forEach((childRule) => processRule(childRule));
      } else {
        processLeafRule(rule);
      }
    };

    processRule(ruleData);
  }

  protected getErrorOutputId(): undefined {
    return undefined;
  }

  protected getPortDisplay(): python.Field | undefined {
    const portDisplayOverridesDict = new Map();

    Array.from(this.workflowContext.portContextById.entries()).forEach(
      ([portId, _], idx) => {
        const conditionData = this.nodeData.data.conditions.find(
          (condition) => condition.sourceHandleId === portId
        );

        if (!conditionData) {
          return;
        }

        const edge = this.workflowContext.workflowRawEdges.find(
          (edge) => edge.sourceHandleId === portId
        );

        if (!edge) {
          return;
        }

        const portName = `branch_${idx + 1}`;

        const portDisplayOverrides = python.instantiateClass({
          classReference: python.reference({
            name: "PortDisplayOverrides",
            modulePath:
              this.workflowContext.sdkModulePathNames
                .NODE_DISPLAY_TYPES_MODULE_PATH,
          }),
          arguments_: [
            python.methodArgument({
              name: "id",
              value: python.TypeInstantiation.uuid(edge.sourceHandleId),
            }),
          ],
        });

        portDisplayOverridesDict.set(portName, portDisplayOverrides);
      }
    );
    return python.field({
      name: "port_displays",
      initializer: python.TypeInstantiation.dict(
        Array.from(portDisplayOverridesDict.entries()).map(([key, value]) => ({
          key: python.reference({
            name: this.nodeContext.nodeClassName,
            modulePath: this.nodeContext.nodeModulePath,
            attribute: [PORTS_CLASS_NAME, key],
          }),
          value: value,
        }))
      ),
    });
  }
}
