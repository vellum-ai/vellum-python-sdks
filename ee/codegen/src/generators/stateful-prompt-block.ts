import { python } from "@fern-api/python-ast";
import { MethodArgument } from "@fern-api/python-ast/MethodArgument";
import { isNil } from "lodash";

import {
  BasePromptBlock,
  PromptTemplateBlockExcludingFunctionDefinition,
} from "src/generators/base-prompt-block";
import {
  ChatMessagePromptTemplateBlock,
  JinjaPromptTemplateBlock,
  PlainTextPromptTemplateBlock,
  RichTextPromptTemplateBlock,
  VariablePromptTemplateBlock,
} from "src/types/vellum";

// Flesh out unit tests for various prompt configurations
// https://app.shortcut.com/vellum/story/5249
export class StatefulPromptBlock extends BasePromptBlock<PromptTemplateBlockExcludingFunctionDefinition> {
  protected generateJinjaPromptBlock(
    promptBlock: JinjaPromptTemplateBlock
  ): python.ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
    ];

    if (promptBlock.properties.template) {
      classArgs.push(
        new MethodArgument({
          name: "template",
          value: python.TypeInstantiation.str(promptBlock.properties.template, {
            multiline: true,
            startOnNewLine: true,
            endWithNewLine: true,
          }),
        })
      );
    } else {
      classArgs.push(
        new MethodArgument({
          name: "template",
          value: python.TypeInstantiation.str(""),
        })
      );
    }

    const jinjaBlock = python.instantiateClass({
      classReference: this.getPromptBlockRef(promptBlock),
      arguments_: classArgs,
    });

    this.inheritReferences(jinjaBlock);
    return jinjaBlock;
  }

  protected generateChatMessagePromptBlock(
    promptBlock: ChatMessagePromptTemplateBlock
  ): python.ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
    ];

    if (promptBlock.properties.chatRole) {
      classArgs.push(
        new MethodArgument({
          name: "chat_role",
          value: python.TypeInstantiation.str(promptBlock.properties.chatRole),
        })
      );
    }

    if (!isNil(promptBlock.properties.chatSource)) {
      classArgs.push(
        new MethodArgument({
          name: "chat_source",
          value: python.TypeInstantiation.str(
            promptBlock.properties.chatSource
          ),
        })
      );
    }

    if (promptBlock.properties.chatMessageUnterminated) {
      classArgs.push(
        new MethodArgument({
          name: "chat_message_unterminated",
          value: python.TypeInstantiation.bool(
            promptBlock.properties.chatMessageUnterminated
          ),
        })
      );
    }

    const childBlocks = promptBlock.properties.blocks.filter(
      (
        block
      ): block is Exclude<
        PromptTemplateBlockExcludingFunctionDefinition,
        PlainTextPromptTemplateBlock
      > => block.blockType !== "FUNCTION_DEFINITION"
    );
    classArgs.push(
      new MethodArgument({
        name: "blocks",
        value: python.TypeInstantiation.list(
          childBlocks.map((block) => {
            return this.generateAstNode(block);
          })
        ),
      })
    );

    const chatBlock = python.instantiateClass({
      classReference: this.getPromptBlockRef(promptBlock),
      arguments_: classArgs,
    });

    this.inheritReferences(chatBlock);
    return chatBlock;
  }

  protected generateVariablePromptBlock(
    promptBlock: VariablePromptTemplateBlock
  ): python.ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
    ];
    const inputVariableName =
      this.inputVariableNameById?.[promptBlock.inputVariableId] ??
      promptBlock.inputVariableId;

    classArgs.push(
      new MethodArgument({
        name: "input_variable",
        value: python.TypeInstantiation.str(inputVariableName),
      })
    );

    const variableBlock = python.instantiateClass({
      classReference: this.getPromptBlockRef(promptBlock),
      arguments_: classArgs,
    });

    this.inheritReferences(variableBlock);
    return variableBlock;
  }

  protected generatePlainTextPromptBlock(
    promptBlock: PlainTextPromptTemplateBlock
  ): python.ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
    ];

    const nonEmpty = promptBlock.text !== "";
    classArgs.push(
      new MethodArgument({
        name: "text",
        value: python.TypeInstantiation.str(promptBlock.text, {
          multiline: nonEmpty,
          startOnNewLine: nonEmpty,
          endWithNewLine: nonEmpty,
        }),
      })
    );

    const plainBlock = python.instantiateClass({
      classReference: this.getPromptBlockRef(promptBlock),
      arguments_: classArgs,
    });

    this.inheritReferences(plainBlock);
    return plainBlock;
  }

  protected generateRichTextPromptBlock(
    promptBlock: RichTextPromptTemplateBlock
  ): python.ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
    ];

    classArgs.push(
      new MethodArgument({
        name: "blocks",
        value: python.TypeInstantiation.list(
          promptBlock.blocks.map((block) => {
            if (block.blockType === "VARIABLE") {
              return this.generateVariablePromptBlock(block);
            } else {
              return this.generatePlainTextPromptBlock(block);
            }
          })
        ),
      })
    );

    const richBlock = python.instantiateClass({
      classReference: this.getPromptBlockRef(promptBlock),
      arguments_: classArgs,
    });

    this.inheritReferences(richBlock);
    return richBlock;
  }
}
