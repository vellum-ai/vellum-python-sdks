import { WorkflowContext } from "src/context";
import { Reference } from "src/generators/extensions/reference";

export declare namespace BaseState {
  export interface Args {
    workflowContext: WorkflowContext;
  }
}

export class BaseState extends Reference {
  public constructor(args: BaseState.Args) {
    super({
      name: "BaseState",
      modulePath: args.workflowContext.sdkModulePathNames.STATE_MODULE_PATH,
    });
  }
}
