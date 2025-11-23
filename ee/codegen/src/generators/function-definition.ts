import { python } from "@fern-api/python-ast";
import { MethodArgument } from "@fern-api/python-ast/MethodArgument";
import { AstNode } from "@fern-api/python-ast/python";
import { isNil } from "lodash";

import { VELLUM_CLIENT_MODULE_PATH } from "src/constants";
import { Writer } from "src/generators/extensions/writer";
import { Json } from "src/generators/json";
import { FunctionDefinitionPromptTemplateBlock } from "src/types/vellum";

export declare namespace FunctionDefinition {
  interface Args {
    functionDefinition: FunctionDefinitionPromptTemplateBlock;
  }
}

export class FunctionDefinition extends AstNode {
  private astNode: python.ClassInstantiation;

  public constructor({ functionDefinition }: FunctionDefinition.Args) {
    super();
    this.astNode = this.generateAstNode(functionDefinition);
  }

  protected generateAstNode(
    functionDefinition: FunctionDefinitionPromptTemplateBlock
  ): python.ClassInstantiation {
    const classArgs: MethodArgument[] = [];

    if (!isNil(functionDefinition.properties.functionName)) {
      classArgs.push(
        new MethodArgument({
          name: "name",
          value: python.TypeInstantiation.str(
            functionDefinition.properties.functionName
          ),
        })
      );
    }

    if (!isNil(functionDefinition.properties.functionDescription)) {
      classArgs.push(
        new MethodArgument({
          name: "description",
          value: python.TypeInstantiation.str(
            functionDefinition.properties.functionDescription
          ),
        })
      );
    }

    if (!isNil(functionDefinition.properties.functionParameters)) {
      classArgs.push(
        new MethodArgument({
          name: "parameters",
          value: new Json(functionDefinition.properties.functionParameters),
        })
      );
    }

    if (!isNil(functionDefinition.properties.functionForced)) {
      classArgs.push(
        new MethodArgument({
          name: "function_forced",
          value: python.TypeInstantiation.bool(
            functionDefinition.properties.functionForced
          ),
        })
      );
    }

    if (!isNil(functionDefinition.properties.functionStrict)) {
      classArgs.push(
        new MethodArgument({
          name: "function_strict",
          value: python.TypeInstantiation.bool(
            functionDefinition.properties.functionStrict
          ),
        })
      );
    }

    const functionDefinitionClass = python.instantiateClass({
      classReference: python.reference({
        name: "FunctionDefinition",
        modulePath: VELLUM_CLIENT_MODULE_PATH,
      }),
      arguments_: classArgs,
    });

    this.inheritReferences(functionDefinitionClass);
    return functionDefinitionClass;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}
