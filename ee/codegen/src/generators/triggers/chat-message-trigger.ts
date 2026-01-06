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

    body.push(...this.createAttributeFields());

    const execConfig = this.trigger.execConfig;
    if (execConfig?.output) {
      body.push(this.createConfigClass(execConfig.output));
    }

    return body;
  }

  private createConfigClass(output: WorkflowOutputWorkflowReference): AstNode {
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

    const outputField = this.createOutputField(output);
    if (outputField) {
      configClass.add(outputField);
    }

    return configClass;
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
