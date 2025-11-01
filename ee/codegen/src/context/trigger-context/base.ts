import { GENERATED_TRIGGERS_MODULE_NAME } from "src/constants";
import { WorkflowContext } from "src/context";
import { WorkflowTrigger } from "src/types/vellum";
import { createPythonClassName } from "src/utils/casing";

export declare namespace BaseTriggerContext {
  interface Args<T extends WorkflowTrigger> {
    workflowContext: WorkflowContext;
    triggerData: T;
  }
}

export abstract class BaseTriggerContext<T extends WorkflowTrigger> {
  public readonly workflowContext: WorkflowContext;
  public readonly triggerData: T;
  public readonly triggerModulePath: string[];
  public readonly triggerModuleName: string;
  public readonly triggerFileName: string;
  public readonly triggerClassName: string;

  constructor(args: BaseTriggerContext.Args<T>) {
    this.workflowContext = args.workflowContext;
    this.triggerData = args.triggerData;

    const { moduleName, className, modulePath } = this.getTriggerModuleInfo();
    this.triggerModuleName = moduleName;
    this.triggerClassName = className;
    this.triggerModulePath = modulePath;
    this.triggerFileName = `${this.triggerModuleName}.py`;
  }

  protected abstract getTriggerModuleInfo(): {
    moduleName: string;
    className: string;
    modulePath: string[];
  };

  public getTriggerId(): string {
    return this.triggerData.id;
  }
}
