import { python } from "@fern-api/python-ast";
import { isNil } from "lodash";

import { VELLUM_CLIENT_MODULE_PATH } from "src/constants";
import {
  BasePromptBlock,
  PromptTemplateBlockExcludingFunctionDefinition,
} from "src/generators/base-prompt-block";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { Json } from "src/generators/json";
import {
  AudioPromptTemplateBlock,
  ChatMessagePromptTemplateBlock,
  DocumentPromptTemplateBlock,
  ImagePromptTemplateBlock,
  JinjaPromptTemplateBlock,
  PlainTextPromptTemplateBlock,
  RichTextPromptTemplateBlock,
  VariablePromptTemplateBlock,
  VideoPromptTemplateBlock,
} from "src/types/vellum";

// Flesh out unit tests for various prompt configurations
// https://app.shortcut.com/vellum/story/5249
export class StatefulPromptBlock extends BasePromptBlock<PromptTemplateBlockExcludingFunctionDefinition> {
  protected generateAstNode(
    promptBlock: PromptTemplateBlockExcludingFunctionDefinition
  ): ClassInstantiation {
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
      case "AUDIO":
        return this.generateAudioPromptBlock(promptBlock);
      case "VIDEO":
        return this.generateVideoPromptBlock(promptBlock);
      case "IMAGE":
        return this.generateImagePromptBlock(promptBlock);
      case "DOCUMENT":
        return this.generateDocumentPromptBlock(promptBlock);
    }
  }

  private getPromptBlockRef(
    promptBlock: PromptTemplateBlockExcludingFunctionDefinition
  ): python.Reference {
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
      case "AUDIO":
        pathName = "AudioPromptBlock";
        break;
      case "VIDEO":
        pathName = "VideoPromptBlock";
        break;
      case "IMAGE":
        pathName = "ImagePromptBlock";
        break;
      case "DOCUMENT":
        pathName = "DocumentPromptBlock";
        break;
    }
    return python.reference({
      name: pathName,
      modulePath: VELLUM_CLIENT_MODULE_PATH,
    });
  }

  private generateJinjaPromptBlock(
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

  private generateChatMessagePromptBlock(
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

    const chatBlock = new ClassInstantiation({
      classReference: this.getPromptBlockRef(promptBlock),
      arguments_: classArgs,
    });

    this.inheritReferences(chatBlock);
    return chatBlock;
  }

  private generateVariablePromptBlock(
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

  private generatePlainTextPromptBlock(
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

  private generateRichTextPromptBlock(
    promptBlock: RichTextPromptTemplateBlock
  ): ClassInstantiation {
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

    const richBlock = new ClassInstantiation({
      classReference: this.getPromptBlockRef(promptBlock),
      arguments_: classArgs,
    });

    this.inheritReferences(richBlock);
    return richBlock;
  }

  private generateCommonFileInputArguments(
    promptBlock:
      | AudioPromptTemplateBlock
      | VideoPromptTemplateBlock
      | ImagePromptTemplateBlock
      | DocumentPromptTemplateBlock
  ): MethodArgument[] {
    const classArgs: MethodArgument[] = [];

    classArgs.push(
      new MethodArgument({
        name: "src",
        value: new StrInstantiation(promptBlock.src),
      })
    );

    if (promptBlock.metadata) {
      const metadataJson = new Json(promptBlock.metadata);
      classArgs.push(
        new MethodArgument({
          name: "metadata",
          value: metadataJson,
        })
      );
    }

    return classArgs;
  }

  private generateAudioPromptBlock(
    promptBlock: AudioPromptTemplateBlock
  ): ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
      ...this.generateCommonFileInputArguments(promptBlock),
    ];

    const audioBlock = new ClassInstantiation({
      classReference: this.getPromptBlockRef(promptBlock),
      arguments_: classArgs,
    });

    this.inheritReferences(audioBlock);
    return audioBlock;
  }

  private generateVideoPromptBlock(
    promptBlock: VideoPromptTemplateBlock
  ): ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
      ...this.generateCommonFileInputArguments(promptBlock),
    ];

    const videoBlock = new ClassInstantiation({
      classReference: this.getPromptBlockRef(promptBlock),
      arguments_: classArgs,
    });

    this.inheritReferences(videoBlock);
    return videoBlock;
  }

  private generateImagePromptBlock(
    promptBlock: ImagePromptTemplateBlock
  ): ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
      ...this.generateCommonFileInputArguments(promptBlock),
    ];

    const imageBlock = new ClassInstantiation({
      classReference: this.getPromptBlockRef(promptBlock),
      arguments_: classArgs,
    });

    this.inheritReferences(imageBlock);
    return imageBlock;
  }

  private generateDocumentPromptBlock(
    promptBlock: DocumentPromptTemplateBlock
  ): ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
      ...this.generateCommonFileInputArguments(promptBlock),
    ];

    const documentBlock = new ClassInstantiation({
      classReference: this.getPromptBlockRef(promptBlock),
      arguments_: classArgs,
    });

    this.inheritReferences(documentBlock);
    return documentBlock;
  }
}
