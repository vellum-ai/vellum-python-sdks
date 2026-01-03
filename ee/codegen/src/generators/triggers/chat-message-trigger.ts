import { VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH } from "src/constants";
import { Class } from "src/generators/extensions/class";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { Field } from "src/generators/extensions/field";
import { LambdaInstantiation } from "src/generators/extensions/lambda-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { Reference } from "src/generators/extensions/reference";
import { BaseTrigger } from "src/generators/triggers/base-trigger";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import { createPythonClassName, toPythonSafeSnakeCase } from "src/utils/casing";

import type { AstNode } from "src/generators/extensions/ast-node";
import type {
  ChatMessageTrigger as ChatMessageTriggerType,
  WorkflowValueDescriptor as WorkflowValueDescriptorType,
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

  protected getTriggerClassBody(): AstNode[] {
    const body: AstNode[] = [];

    // Add attribute fields
    body.push(...this.createAttributeFields());

    // Create Config class if execConfig.output is present
    const execConfig = this.trigger.execConfig;
    if (execConfig?.output) {
      body.push(this.createConfigClass(execConfig.output));
    }

    return body;
  }

  private createConfigClass(
    output: NonNullable<ChatMessageTriggerType["execConfig"]>["output"]
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

    return configClass;
  }

  private createOutputField(
    output: WorkflowValueDescriptorType
  ): AstNode | undefined {
    const workflowValueDescriptor = new WorkflowValueDescriptor({
      workflowContext: this.workflowContext,
      workflowValueDescriptor: output,
    });

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
          value: new LambdaInstantiation({
            body: workflowValueDescriptor,
          }),
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
