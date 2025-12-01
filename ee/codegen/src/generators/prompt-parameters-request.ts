import { python } from "@fern-api/python-ast";
import { isNil } from "lodash";
import { PromptParameters as PromptParametersType } from "vellum-ai/api";

import { VELLUM_CLIENT_MODULE_PATH } from "src/constants";
import { AstNode } from "src/generators/extensions/ast-node";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { ListInstantiation } from "src/generators/extensions/list-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { NoneInstantiation } from "src/generators/extensions/none-instantiation";
import { Reference } from "src/generators/extensions/reference";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { Writer } from "src/generators/extensions/writer";
import { Json } from "src/generators/json";

export declare namespace PromptParameters {
  interface Args {
    promptParametersRequest: PromptParametersType;
  }
}

export class PromptParameters extends AstNode {
  private promptParametersRequest: PromptParametersType;
  private astNode: AstNode;

  public constructor({ promptParametersRequest }: PromptParameters.Args) {
    super();
    this.promptParametersRequest = promptParametersRequest;
    this.astNode = this.generatePromptParameters();
    this.inheritReferences(this.astNode);
  }

  private getPromptParametersRef(): Reference {
    return new Reference({
      name: "PromptParameters",
      modulePath: VELLUM_CLIENT_MODULE_PATH,
    });
  }

  private generatePromptParameters(): ClassInstantiation {
    const classArgs: MethodArgument[] = [];

    const stopValue = new ListInstantiation(
      (this.promptParametersRequest.stop ?? []).map(
        (str) => new StrInstantiation(str)
      )
    );
    classArgs.push(
      new MethodArgument({
        name: "stop",
        value: stopValue,
      })
    );

    const temperatureValue = isNil(this.promptParametersRequest.temperature)
      ? new NoneInstantiation()
      : python.TypeInstantiation.float(
          this.promptParametersRequest.temperature
        );
    classArgs.push(
      new MethodArgument({
        name: "temperature",
        value: temperatureValue,
      })
    );

    const maxTokensValue = isNil(this.promptParametersRequest.maxTokens)
      ? new NoneInstantiation()
      : python.TypeInstantiation.float(this.promptParametersRequest.maxTokens);
    classArgs.push(
      new MethodArgument({
        name: "max_tokens",
        value: maxTokensValue,
      })
    );

    const topPValue = isNil(this.promptParametersRequest.topP)
      ? new NoneInstantiation()
      : python.TypeInstantiation.float(this.promptParametersRequest.topP);
    classArgs.push(
      new MethodArgument({
        name: "top_p",
        value: topPValue,
      })
    );

    const topKValue = isNil(this.promptParametersRequest.topK)
      ? new NoneInstantiation()
      : python.TypeInstantiation.float(this.promptParametersRequest.topK);
    classArgs.push(
      new MethodArgument({
        name: "top_k",
        value: topKValue,
      })
    );

    const frequencyPenaltyValue = isNil(
      this.promptParametersRequest.frequencyPenalty
    )
      ? new NoneInstantiation()
      : python.TypeInstantiation.float(
          this.promptParametersRequest.frequencyPenalty
        );
    classArgs.push(
      new MethodArgument({
        name: "frequency_penalty",
        value: frequencyPenaltyValue,
      })
    );

    const presencePenaltyValue = isNil(
      this.promptParametersRequest.presencePenalty
    )
      ? new NoneInstantiation()
      : python.TypeInstantiation.float(
          this.promptParametersRequest.presencePenalty
        );
    classArgs.push(
      new MethodArgument({
        name: "presence_penalty",
        value: presencePenaltyValue,
      })
    );

    const logitBiasValue = new Json(this.promptParametersRequest.logitBias);
    classArgs.push(
      new MethodArgument({
        name: "logit_bias",
        value: logitBiasValue,
      })
    );

    const custom_parameters_value = new Json(
      this.promptParametersRequest.customParameters
    );
    classArgs.push(
      new MethodArgument({
        name: "custom_parameters",
        value: custom_parameters_value,
      })
    );

    const clazz = new ClassInstantiation({
      classReference: this.getPromptParametersRef(),
      arguments_: classArgs,
    });
    this.inheritReferences(clazz);
    return clazz;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}
