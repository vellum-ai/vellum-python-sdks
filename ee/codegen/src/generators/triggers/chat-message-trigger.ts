import { VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH } from "src/constants";
import { Class } from "src/generators/extensions/class";
import { Field } from "src/generators/extensions/field";
import { Reference } from "src/generators/extensions/reference";
import { BaseTrigger } from "src/generators/triggers/base-trigger";
import { WorkflowOutputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/workflow-output-workflow-reference";
import { createPythonClassName, toPythonSafeSnakeCase } from "src/utils/casing";

import type { AstNode } from "src/generators/extensions/ast-node";
import type {
  ChatMessageTrigger as ChatMessageTriggerType,
  WorkflowOutputWorkflowReference as WorkflowOutputWorkflowReferenceType,
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

  private createConfigClass(
    output: WorkflowOutputWorkflowReferenceType
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

    const outputField = this.createOutputField(output);
    if (outputField) {
      configClass.add(outputField);
    }

    return configClass;
  }

  private createOutputField(
    output: WorkflowOutputWorkflowReferenceType
  ): AstNode | undefined {
    const workflowOutputReference = new WorkflowOutputWorkflowReference({
      workflowContext: this.workflowContext,
      nodeInputWorkflowReferencePointer: output,
    });

    const astNode = workflowOutputReference.getAstNode();
    if (!astNode) {
      return undefined;
    }

    this.inheritReferences(workflowOutputReference);

    return new Field({
      name: "output",
      initializer: astNode,
    });
  }
}
