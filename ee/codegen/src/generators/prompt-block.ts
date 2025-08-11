import { python } from "@fern-api/python-ast";
import { ClassInstantiation } from "@fern-api/python-ast/ClassInstantiation";
import { MethodArgument } from "@fern-api/python-ast/MethodArgument";
import { isNil } from "lodash";
import {
  ChatMessagePromptBlock,
  JinjaPromptBlock,
  PlainTextPromptBlock,
  RichTextPromptBlock,
  VariablePromptBlock,
} from "vellum-ai/api";

import { VELLUM_CLIENT_MODULE_PATH } from "src/constants";
import {
  BasePromptBlock,
  PromptBlock as PromptBlockType,
} from "src/generators/base-prompt-block";

export class PromptBlock extends BasePromptBlock<PromptBlockType> {
  protected generateAstNode(promptBlock: PromptBlockType): ClassInstantiation {
    switch (promptBlock.blockType) {
      case "JINJA":
        return this.generateJinjaPromptBlock(promptBlock);
      case "CHAT_MESSAGE":
        return this.generateChatMessagePromptBlock(promptBlock);
      case "VARIABLE":
        return this.generateVariablePromptBlock(promptBlock);
      case "RICH_TEXT":
        return this.generateRichTextPromptBlock(promptBlock);
      case "PLAIN_TEXT":
        return this.generatePlainTextPromptBlock(promptBlock);
    }
  }

  private getPromptBlockRef(promptBlock: PromptBlockType): python.Reference {
    let pathName;
    switch (promptBlock.blockType) {
      case "JINJA":
        pathName = "JinjaPromptBlock";
        break;
      case "CHAT_MESSAGE":
        pathName = "ChatMessagePromptBlock";
        break;
      case "VARIABLE":
        pathName = "VariablePromptBlock";
        break;
      case "RICH_TEXT":
        pathName = "RichTextPromptBlock";
        break;
      case "PLAIN_TEXT":
        pathName = "PlainTextPromptBlock";
        break;
    }
    return python.reference({
      name: pathName,
      modulePath: VELLUM_CLIENT_MODULE_PATH,
    });
  }

  private generateJinjaPromptBlock(
    promptBlock: JinjaPromptBlock
  ): python.ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
    ];

    if (promptBlock.template) {
      classArgs.push(
        new MethodArgument({
          name: "template",
          value: python.TypeInstantiation.str(promptBlock.template, {
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

  private generateChatMessagePromptBlock(
    promptBlock: ChatMessagePromptBlock
  ): python.ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
    ];

    if (promptBlock.chatRole) {
      classArgs.push(
        new MethodArgument({
          name: "chat_role",
          value: python.TypeInstantiation.str(promptBlock.chatRole),
        })
      );
    }

    if (!isNil(promptBlock.chatSource)) {
      classArgs.push(
        new MethodArgument({
          name: "chat_source",
          value: python.TypeInstantiation.str(promptBlock.chatSource),
        })
      );
    }

    if (promptBlock.chatMessageUnterminated) {
      classArgs.push(
        new MethodArgument({
          name: "chat_message_unterminated",
          value: python.TypeInstantiation.bool(
            promptBlock.chatMessageUnterminated
          ),
        })
      );
    }

    // TODO: Other types of blocks
    const childBlocks = promptBlock.blocks as PromptBlockType[];
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

  private generateVariablePromptBlock(
    promptBlock: VariablePromptBlock
  ): python.ClassInstantiation {
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

  private generatePlainTextPromptBlock(
    promptBlock: PlainTextPromptBlock
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

  private generateRichTextPromptBlock(
    promptBlock: RichTextPromptBlock
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
