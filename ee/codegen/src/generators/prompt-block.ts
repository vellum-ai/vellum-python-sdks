import { isNil } from "lodash";
import {
  ChatMessagePromptBlock,
  JinjaPromptBlock,
  PlainTextPromptBlock,
  RichTextPromptBlock,
  VariablePromptBlock,
} from "vellum-ai/api";

import {
  BasePromptBlock,
  PromptBlock as PromptBlockType,
} from "src/generators/base-prompt-block";
import { BoolInstantiation } from "src/generators/extensions/bool-instantiation";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { ListInstantiation } from "src/generators/extensions/list-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";

export class PromptBlock extends BasePromptBlock<PromptBlockType> {
  protected generateJinjaPromptBlock(
    promptBlock: JinjaPromptBlock
  ): ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
    ];

    if (promptBlock.template) {
      classArgs.push(
        new MethodArgument({
          name: "template",
          value: new StrInstantiation(promptBlock.template, {
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
    promptBlock: ChatMessagePromptBlock
  ): ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
    ];

    if (promptBlock.chatRole) {
      classArgs.push(
        new MethodArgument({
          name: "chat_role",
          value: new StrInstantiation(promptBlock.chatRole),
        })
      );
    }

    if (!isNil(promptBlock.chatSource)) {
      classArgs.push(
        new MethodArgument({
          name: "chat_source",
          value: new StrInstantiation(promptBlock.chatSource),
        })
      );
    }

    if (promptBlock.chatMessageUnterminated) {
      classArgs.push(
        new MethodArgument({
          name: "chat_message_unterminated",
          value: new BoolInstantiation(promptBlock.chatMessageUnterminated),
        })
      );
    }

    const childBlocks = promptBlock.blocks as PromptBlockType[];
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
    promptBlock: VariablePromptBlock
  ): ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
    ];

    // Use the mapping to convert ID to key, fallback to original value if not found
    const inputVariableName =
      this.inputVariableNameById?.[promptBlock.inputVariable] ??
      promptBlock.inputVariable;

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
    promptBlock: PlainTextPromptBlock
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
    promptBlock: RichTextPromptBlock
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
