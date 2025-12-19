import { python } from "@fern-api/python-ast";

import { PORTS_CLASS_NAME } from "src/constants";
import { ConditionalNodeContext } from "src/context/node-context/conditional-node";
import { ConditionalNodePort } from "src/generators/conditional-node-port";
import { AstNode } from "src/generators/extensions/ast-node";
import { Class } from "src/generators/extensions/class";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { DictInstantiation } from "src/generators/extensions/dict-instantiation";
import { Field } from "src/generators/extensions/field";
import { IntInstantiation } from "src/generators/extensions/int-instantiation";
import { ListInstantiation } from "src/generators/extensions/list-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { NoneInstantiation } from "src/generators/extensions/none-instantiation";
import { Reference } from "src/generators/extensions/reference";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { BaseNode } from "src/generators/nodes/bases/base";
import {
  ConditionalNodeData,
  ConditionalNode as ConditionalNodeType,
  ConditionalRuleData,
} from "src/types/vellum";
import { isNilOrEmpty } from "src/utils/typing";

export class ConditionalNode extends BaseNode<
  ConditionalNodeType,
  ConditionalNodeContext
> {
  protected DEFAULT_TRIGGER = "AWAIT_ANY";
  protected getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    if (isNilOrEmpty(this.nodeData.ports)) {
      const inputFieldKeysByRuleId = new Map<string, string>();
      const valueInputKeysByRuleId = new Map<string, string>();
      this.constructMapContextForAllConditions(
        inputFieldKeysByRuleId,
        valueInputKeysByRuleId,
        this.nodeData.data
      );

      const baseNodeClassRef = this.getNodeBaseClass();

      const ref = new Reference({
        name: baseNodeClassRef.name,
        modulePath: baseNodeClassRef.modulePath,
        alias: baseNodeClassRef.alias,
        attribute: ["Ports"],
      });

      this.getNodeBaseClass().inheritReferences(ref);

      const portsClass = new Class({
        name: "Ports",
        extends_: [ref],
      });
      Array.from(this.workflowContext.portContextById.entries()).forEach(
        ([portId, context]) => {
          const conditionDataWithIndex = [
            ...this.nodeData.data.conditions.entries(),
          ].find(([_, condition]) => condition.sourceHandleId === portId);

          if (!conditionDataWithIndex) {
            return;
          }

          portsClass.addField(
            new Field({
              name: context.portName,
              initializer: new ConditionalNodePort({
                portContext: context,
                inputFieldKeysByRuleId: inputFieldKeysByRuleId,
                valueInputKeysByRuleId: valueInputKeysByRuleId,
                conditionDataWithIndex: conditionDataWithIndex,
                nodeInputsByKey: this.nodeInputsByKey,
                nodeLabel: this.nodeData.data.label,
              }),
            })
          );
        }
      );
      statements.push(portsClass);
    }
    return statements;
  }

  protected getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    statements.push(
      new Field({
        name: "target_handle_id",
        initializer: python.TypeInstantiation.uuid(
          this.nodeData.data.targetHandleId
        ),
      })
    );

    statements.push(
      new Field({
        name: "source_handle_ids",
        initializer: new DictInstantiation(
          this.nodeData.data.conditions.map((condition, idx) => ({
            key: new IntInstantiation(idx),
            value: python.TypeInstantiation.uuid(condition.sourceHandleId),
          }))
        ),
      })
    );

    const ruleIdMapRef = new Reference({
      name: "RuleIdMap",
      modulePath: [
        ...this.workflowContext.sdkModulePathNames.NODE_DISPLAY_MODULE_PATH,
        "vellum",
        "conditional_node",
      ],
    });

    this.getNodeDisplayBaseClass().inheritReferences(ruleIdMapRef);

    statements.push(
      new Field({
        name: "rule_ids",
        initializer: new ListInstantiation(
          this.createRuleIdMapList(this.nodeData.data, ruleIdMapRef)
        ),
      })
    );

    const conditionIdRef = new Reference({
      name: "ConditionId",
      modulePath: [
        ...this.workflowContext.sdkModulePathNames.NODE_DISPLAY_MODULE_PATH,
        "vellum",
        "conditional_node",
      ],
    });

    this.getNodeDisplayBaseClass().inheritReferences(conditionIdRef);

    statements.push(
      new Field({
        name: "condition_ids",
        initializer: new ListInstantiation(
          this.createConditionIdList(this.nodeData.data, conditionIdRef)
        ),
      })
    );

    return statements;
  }

  protected getOutputDisplay(): Field | undefined {
    return undefined;
  }

  private createConditionIdList(
    nodeData: ConditionalNodeData,
    conditionIdRef: Reference
  ): AstNode[] {
    const conditionIdsList: AstNode[] = [];
    nodeData.conditions.forEach((condition) => {
      conditionIdsList.push(
        new ClassInstantiation({
          classReference: conditionIdRef,
          arguments_: [
            new MethodArgument({
              name: "id",
              value: new StrInstantiation(condition.id),
            }),
            new MethodArgument({
              name: "rule_group_id",
              value: condition.data
                ? new StrInstantiation(condition.data.id)
                : new NoneInstantiation(),
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

    return new ClassInstantiation({
      classReference: ruleIdMapRef,
      arguments_: [
        new MethodArgument({
          name: "id",
          value: new StrInstantiation(ruleData.id),
        }),
        new MethodArgument({
          name: "lhs",
          value: lhs ? lhs : new NoneInstantiation(),
        }),
        new MethodArgument({
          name: "rhs",
          value: rhs ? rhs : new NoneInstantiation(),
        }),
        new MethodArgument({
          name: "field_node_input_id",
          value: fieldId
            ? new StrInstantiation(fieldId)
            : new NoneInstantiation(),
        }),
        new MethodArgument({
          name: "value_node_input_id",
          value: valueId
            ? new StrInstantiation(valueId)
            : new NoneInstantiation(),
        }),
      ],
    });
  }

  private constructMapContextForAllConditions(
    inputFieldKeysByRuleId: Map<string, string>,
    valueInputKeysByRuleId: Map<string, string>,
    nodeData: ConditionalNodeData
  ): void {
    nodeData.conditions.forEach((condition) => {
      if (condition.data) {
        this.constructMapContextByRuleIds(
          inputFieldKeysByRuleId,
          valueInputKeysByRuleId,
          condition.data
        );
      }
    });
  }

  private constructMapContextByRuleIds(
    inputFieldsByRuleId: Map<string, string>,
    valueInputsByRuleIds: Map<string, string>,
    ruleData: ConditionalRuleData
  ): void {
    if (!ruleData) {
      return;
    }
    if (isNilOrEmpty(ruleData.rules) && ruleData.fieldNodeInputId) {
      this.nodeData.inputs.forEach((input) => {
        if (input.id === ruleData.fieldNodeInputId) {
          inputFieldsByRuleId.set(ruleData.id, input.key);
        }
        if (
          ruleData.valueNodeInputId &&
          input.id === ruleData.valueNodeInputId
        ) {
          valueInputsByRuleIds.set(ruleData.id, input.key);
        }
      });
    }

    if (ruleData.rules) {
      ruleData.rules.forEach((rule) => {
        this.constructMapContextByRuleIds(
          inputFieldsByRuleId,
          valueInputsByRuleIds,
          rule
        );
      });
    }
  }

  protected getErrorOutputId(): undefined {
    return undefined;
  }

  protected getPortDisplay(): Field | undefined {
    if (this.nodeData.ports) {
      return super.getPortDisplay();
    } else {
      const portDisplayOverridesDict = new Map();

      Array.from(this.workflowContext.portContextById.entries()).forEach(
        ([portId, context]) => {
          const conditionData = this.nodeData.data.conditions.find(
            (condition) => condition.sourceHandleId === portId
          );

          if (!conditionData) {
            return;
          }

          const edge = this.workflowContext.workflowRawData.edges.find(
            (edge) => edge.sourceHandleId === portId
          );

          if (!edge) {
            return;
          }

          const portDisplayOverrides = new ClassInstantiation({
            classReference: new Reference({
              name: "PortDisplayOverrides",
              modulePath:
                this.workflowContext.sdkModulePathNames
                  .NODE_DISPLAY_TYPES_MODULE_PATH,
            }),
            arguments_: [
              new MethodArgument({
                name: "id",
                value: python.TypeInstantiation.uuid(edge.sourceHandleId),
              }),
            ],
          });

          portDisplayOverridesDict.set(context.portName, portDisplayOverrides);
        }
      );
      return new Field({
        name: "port_displays",
        initializer: new DictInstantiation(
          Array.from(portDisplayOverridesDict.entries()).map(
            ([key, value]) => ({
              key: new Reference({
                name: this.nodeContext.nodeClassName,
                modulePath: this.nodeContext.nodeModulePath,
                attribute: [PORTS_CLASS_NAME, key],
              }),
              value: value,
            })
          )
        ),
      });
    }
  }
}
