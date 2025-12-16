import { isNil } from "lodash";

import {
  BasePromptBlock,
  PromptTemplateBlockExcludingFunctionDefinition,
} from "src/generators/base-prompt-block";
import { BoolInstantiation } from "src/generators/extensions/bool-instantiation";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { ListInstantiation } from "src/generators/extensions/list-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
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
  ): ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
    ];

    if (promptBlock.properties.template) {
      classArgs.push(
        new MethodArgument({
          name: "template",
          value: new StrInstantiation(promptBlock.properties.template, {
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
          value: new StrInstantiation(""),
        })
      );
    }

    const jinjaBlock = new ClassInstantiation({
      classReference: this.getPromptBlockRef(promptBlock),
      arguments_: classArgs,
    });

    this.inheritReferences(jinjaBlock);
    return jinjaBlock;
  }

  protected generateChatMessagePromptBlock(
    promptBlock: ChatMessagePromptTemplateBlock
  ): ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
    ];

    if (promptBlock.properties.chatRole) {
      classArgs.push(
        new MethodArgument({
          name: "chat_role",
          value: new StrInstantiation(promptBlock.properties.chatRole),
        })
      );
    }

    if (!isNil(promptBlock.properties.chatSource)) {
      classArgs.push(
        new MethodArgument({
          name: "chat_source",
          value: new StrInstantiation(promptBlock.properties.chatSource),
        })
      );
    }

    if (promptBlock.properties.chatMessageUnterminated) {
      classArgs.push(
        new MethodArgument({
          name: "chat_message_unterminated",
          value: new BoolInstantiation(
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
        value: new ListInstantiation(
          childBlocks.map((block) => {
            return this.generateAstNode(block);
          })
        ),
      })
    );

    const chatBlock = new ClassInstantiation({
      classReference: this.getPromptBlockRef(promptBlock),
      arguments_: classArgs,
    });

    this.inheritReferences(chatBlock);
    return chatBlock;
  }

  protected generateVariablePromptBlock(
    promptBlock: VariablePromptTemplateBlock
  ): ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
    ];
    const inputVariableName =
      this.inputVariableNameById?.[promptBlock.inputVariableId] ??
      promptBlock.inputVariableId;

    classArgs.push(
      new MethodArgument({
        name: "input_variable",
        value: new StrInstantiation(inputVariableName),
      })
    );

    const variableBlock = new ClassInstantiation({
      classReference: this.getPromptBlockRef(promptBlock),
      arguments_: classArgs,
    });

    this.inheritReferences(variableBlock);
    return variableBlock;
  }

  protected generatePlainTextPromptBlock(
    promptBlock: PlainTextPromptTemplateBlock
  ): ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
    ];

    const nonEmpty = promptBlock.text !== "";
    classArgs.push(
      new MethodArgument({
        name: "text",
        value: new StrInstantiation(promptBlock.text, {
          multiline: nonEmpty,
          startOnNewLine: nonEmpty,
          endWithNewLine: nonEmpty,
        }),
      })
    );

    const plainBlock = new ClassInstantiation({
      classReference: this.getPromptBlockRef(promptBlock),
      arguments_: classArgs,
    });

    this.inheritReferences(plainBlock);
    return plainBlock;
  }

  protected generateRichTextPromptBlock(
    promptBlock: RichTextPromptTemplateBlock
  ): ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
    ];

    classArgs.push(
      new MethodArgument({
        name: "blocks",
        value: new ListInstantiation(
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

    const richBlock = new ClassInstantiation({
      classReference: this.getPromptBlockRef(promptBlock),
      arguments_: classArgs,
    });

    this.inheritReferences(richBlock);
    return richBlock;
  }
}
