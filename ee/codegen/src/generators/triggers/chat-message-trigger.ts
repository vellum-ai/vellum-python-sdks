import { VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH } from "src/constants";
import { Class } from "src/generators/extensions/class";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { Field } from "src/generators/extensions/field";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { Reference } from "src/generators/extensions/reference";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { BaseTrigger } from "src/generators/triggers/base-trigger";
import { createPythonClassName, toPythonSafeSnakeCase } from "src/utils/casing";

import type { AstNode } from "src/generators/extensions/ast-node";
import type {
  ChatMessageTrigger as ChatMessageTriggerType,
  ChatMessageTriggerStateReference,
  WorkflowOutputWorkflowReference,
} from "src/types/vellum";

export declare namespace ChatMessageTriggerGenerator {
  interface Args {
    workflowContext: BaseTrigger.Args<ChatMessageTriggerType>["workflowContext"];
    trigger: ChatMessageTriggerType;
  }
}

export class ChatMessageTrigger extends BaseTrigger<ChatMessageTriggerType> {
  protected generateClassName(): string {
    const label = this.trigger.displayData?.label || "ChatMessageTrigger";
    return createPythonClassName(label, {
      force: true,
    });
  }

  protected getModuleName(): string {
    const label = this.trigger.displayData?.label || "chat_message";
    return toPythonSafeSnakeCase(label);
  }

  protected getBaseTriggerClassName(): string {
    return "ChatMessageTrigger";
  }

  protected createAttributeFields(): AstNode[] {
    // Don't generate attribute fields for ChatMessageTrigger (message is handled internally)
    return [];
  }

  protected getTriggerClassBody(): AstNode[] {
    const body: AstNode[] = [];

    // Note: We don't call createAttributeFields() here because the `message` attribute
    // is inherited from the Python ChatMessageTrigger base class

    const execConfig = this.trigger.execConfig;
    const hasOutput = execConfig?.output;
    const hasState = execConfig?.state;

    if (hasOutput || hasState) {
      body.push(this.createConfigClass(execConfig?.output, execConfig?.state));
    }

    return body;
  }

  private createConfigClass(
    output?: WorkflowOutputWorkflowReference,
    state?: ChatMessageTriggerStateReference
  ): AstNode {
    const configClass = new Class({
      name: "Config",
      extends_: [
        new Reference({
          name: "ChatMessageTrigger",
          modulePath: VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH,
          attribute: ["Config"],
        }),
      ],
    });

    if (output) {
      const outputField = this.createOutputField(output);
      if (outputField) {
        configClass.add(outputField);
      }
    }

    if (state) {
      const stateField = this.createStateField(state);
      if (stateField) {
        configClass.add(stateField);
      }
    }

    return configClass;
  }

  private createStateField(
    state: ChatMessageTriggerStateReference
  ): AstNode | undefined {
    const stateVariableContext = this.workflowContext.findStateVariableContextById(
      state.stateVariableId
    );

    if (!stateVariableContext) {
      return undefined;
    }

    const stateReference = new Reference({
      name: "State",
      modulePath: stateVariableContext.definition.module,
      attribute: [stateVariableContext.name],
    });

    this.inheritReferences(stateReference);

    return new Field({
      name: "state",
      initializer: stateReference,
    });
  }

  private createOutputField(
    output: WorkflowOutputWorkflowReference
  ): AstNode | undefined {
    const outputVariableContext =
      this.workflowContext.findOutputVariableContextById(
        output.outputVariableId
      );

    if (!outputVariableContext) {
      return undefined;
    }

    const stringPath = `${this.workflowContext.workflowClassName}.Outputs.${outputVariableContext.name}`;
    const lazyReferenceValue = new ClassInstantiation({
      classReference: new Reference({
        name: "LazyReference",
        modulePath: [
          ...this.workflowContext.sdkModulePathNames.WORKFLOWS_MODULE_PATH,
          "references",
        ],
      }),
      arguments_: [
        new MethodArgument({
          value: new StrInstantiation(stringPath),
        }),
      ],
    });

    this.inheritReferences(lazyReferenceValue);

    return new Field({
      name: "output",
      initializer: lazyReferenceValue,
    });
  }
}
