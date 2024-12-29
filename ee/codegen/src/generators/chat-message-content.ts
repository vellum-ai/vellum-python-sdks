import { python } from "@fern-api/python-ast";
import { MethodArgument } from "@fern-api/python-ast/MethodArgument";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";
import { isNil } from "lodash";
import {
  ChatMessageContentRequest as ChatMessageContentRequestType,
  ChatMessageContent as ChatMessageContentType,
  FunctionCallChatMessageContentValueRequest as FunctionCallChatMessageContentValueRequestType,
  FunctionCallChatMessageContentValue as FunctionCallChatMessageContentValueType,
  ArrayChatMessageContentItemRequest as ArrayChatMessageContentItemRequestType,
  ArrayChatMessageContentItem as ArrayChatMessageContentItemType,
  VellumImage as VellumImageType,
  VellumImageRequest as VellumImageRequestType,
  VellumAudio as VellumAudioType,
  VellumAudioRequest as VellumAudioRequestType,
} from "vellum-ai/api";

import { VELLUM_CLIENT_MODULE_PATH } from "src/constants";
import { Json } from "src/generators/json";
import { assertUnreachable } from "src/utils/typing";

class StringChatMessageContent extends AstNode {
  private astNode: AstNode;

  public constructor(value: string, isRequestType: boolean) {
    super();
    this.astNode = this.generateAstNode(value, isRequestType);
  }

  private generateAstNode(value: string, isRequestType: boolean): AstNode {
    const astNode = python.instantiateClass({
      classReference: python.reference({
        name: "StringChatMessageContent" + (isRequestType ? "Request" : ""),
        modulePath: VELLUM_CLIENT_MODULE_PATH,
      }),
      arguments_: [
        python.methodArgument({
          name: "value",
          value: python.TypeInstantiation.str(value),
        }),
      ],
    });
    this.inheritReferences(astNode);
    return astNode;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}

class FunctionCallChatMessageContentValue extends AstNode {
  private astNode: AstNode;

  public constructor(
    value:
      | FunctionCallChatMessageContentValueRequestType
      | FunctionCallChatMessageContentValueType,
    isRequestType: boolean
  ) {
    super();
    this.astNode = this.generateAstNode(value, isRequestType);
  }

  private generateAstNode(
    value:
      | FunctionCallChatMessageContentValueRequestType
      | FunctionCallChatMessageContentValueType,
    isRequestType: boolean
  ): AstNode {
    const functionCallChatMessageContentValueArgs: MethodArgument[] = [];

    if (value.id !== undefined) {
      functionCallChatMessageContentValueArgs.push(
        new MethodArgument({
          name: "id",
          value: python.TypeInstantiation.str(value.id),
        })
      );
    }

    functionCallChatMessageContentValueArgs.push(
      new MethodArgument({
        name: "name",
        value: python.TypeInstantiation.str(value.name),
      })
    );

    if (value.arguments !== undefined) {
      functionCallChatMessageContentValueArgs.push(
        new MethodArgument({
          name: "arguments",
          value: new Json(value.arguments),
        })
      );
    }

    const functionCallChatMessageContentValueRequestRef = python.reference({
      name:
        "FunctionCallChatMessageContentValue" +
        (isRequestType ? "Request" : ""),
      modulePath: VELLUM_CLIENT_MODULE_PATH,
    });

    const functionCallChatMessageContentValueInstance = python.instantiateClass(
      {
        classReference: functionCallChatMessageContentValueRequestRef,
        arguments_: functionCallChatMessageContentValueArgs,
      }
    );

    const astNode = python.instantiateClass({
      classReference: python.reference({
        name:
          "FunctionCallChatMessageContent" + (isRequestType ? "Request" : ""),
        modulePath: VELLUM_CLIENT_MODULE_PATH,
      }),
      arguments_: [
        new MethodArgument({
          name: "value",
          value: functionCallChatMessageContentValueInstance,
        }),
      ],
    });
    this.inheritReferences(astNode);
    return astNode;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}

class ArrayChatMessageContent extends AstNode {
  private astNode: AstNode;

  public constructor(
    value:
      | ArrayChatMessageContentItemRequestType[]
      | ArrayChatMessageContentItemType[],
    isRequestType: boolean
  ) {
    super();
    this.astNode = this.generateAstNode(value, isRequestType);
  }

  private generateAstNode(
    value:
      | ArrayChatMessageContentItemRequestType[]
      | ArrayChatMessageContentItemType[],
    isRequestType: boolean
  ): AstNode {
    const arrayElements = value.map(
      (element) =>
        new ChatMessageContent({
          chatMessageContent: element as ChatMessageContentRequestType,
        })
    );
    const astNode = python.instantiateClass({
      classReference: python.reference({
        name: "ArrayChatMessageContent" + (isRequestType ? "Request" : ""),
        modulePath: VELLUM_CLIENT_MODULE_PATH,
      }),
      arguments_: [
        python.methodArgument({
          name: "value",
          value: python.TypeInstantiation.list(arrayElements, {
            endWithComma: true,
          }),
        }),
      ],
    });
    this.inheritReferences(astNode);
    return astNode;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}

class ImageChatMessageContent extends AstNode {
  private astNode: AstNode;

  public constructor(
    value: VellumImageType | VellumImageRequestType,
    isRequestType: boolean
  ) {
    super();
    this.astNode = this.generateAstNode(value, isRequestType);
  }

  private generateAstNode(
    value: VellumImageType | VellumImageRequestType,
    isRequestType: boolean
  ): AstNode {
    const imageChatMessageContentRequestRef = python.reference({
      name: "ImageChatMessageContent" + (isRequestType ? "Request" : ""),
      modulePath: VELLUM_CLIENT_MODULE_PATH,
    });

    const arguments_ = [
      python.methodArgument({
        name: "src",
        value: python.TypeInstantiation.str(value.src),
      }),
    ];

    if (!isNil(value.metadata)) {
      const metadataJson = new Json(value.metadata);
      arguments_.push(
        python.methodArgument({
          name: "metadata",
          value: metadataJson,
        })
      );
    }

    const astNode = python.instantiateClass({
      classReference: imageChatMessageContentRequestRef,
      arguments_: arguments_,
    });
    this.inheritReferences(astNode);
    return astNode;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}

class AudioChatMessageContent extends AstNode {
  private astNode: AstNode;

  public constructor(
    value: VellumAudioType | VellumAudioRequestType,
    isRequestType: boolean
  ) {
    super();
    this.astNode = this.generateAstNode(value, isRequestType);
  }

  private generateAstNode(
    value: VellumAudioType | VellumAudioRequestType,
    isRequestType: boolean
  ): AstNode {
    const audioChatMessageContentRequestRef = python.reference({
      name: "AudioChatMessageContent" + (isRequestType ? "Request" : ""),
      modulePath: VELLUM_CLIENT_MODULE_PATH,
    });

    const arguments_ = [
      python.methodArgument({
        name: "src",
        value: python.TypeInstantiation.str(value.src),
      }),
    ];

    if (!isNil(value.metadata)) {
      const metadataJson = new Json(value.metadata);
      arguments_.push(
        python.methodArgument({
          name: "metadata",
          value: metadataJson,
        })
      );
    }

    const astNode = python.instantiateClass({
      classReference: audioChatMessageContentRequestRef,
      arguments_: arguments_,
    });
    this.inheritReferences(astNode);
    return astNode;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}

export namespace ChatMessageContent {
  export interface Args {
    chatMessageContent: ChatMessageContentRequestType | ChatMessageContentType;
    isRequestType?: boolean;
  }
}

export class ChatMessageContent extends AstNode {
  private astNode: AstNode;

  public constructor({
    chatMessageContent,
    isRequestType = false,
  }: ChatMessageContent.Args) {
    super();
    this.astNode = this.generateAstNode(chatMessageContent, isRequestType);
  }

  private generateAstNode(
    chatMessageContent: ChatMessageContentRequestType | ChatMessageContentType,
    isRequestType: boolean
  ): AstNode {
    let astNode: AstNode;

    const contentType = chatMessageContent.type;
    switch (contentType) {
      case "STRING": {
        astNode = new StringChatMessageContent(
          chatMessageContent.value,
          isRequestType
        );
        break;
      }
      case "FUNCTION_CALL": {
        astNode = new FunctionCallChatMessageContentValue(
          chatMessageContent.value,
          isRequestType
        );
        break;
      }
      case "ARRAY": {
        astNode = new ArrayChatMessageContent(
          chatMessageContent.value,
          isRequestType
        );
        break;
      }
      case "IMAGE": {
        astNode = new ImageChatMessageContent(
          chatMessageContent.value,
          isRequestType
        );
        break;
      }
      case "AUDIO": {
        astNode = new AudioChatMessageContent(
          chatMessageContent.value,
          isRequestType
        );
        break;
      }
      default: {
        assertUnreachable(contentType);
      }
    }

    this.inheritReferences(astNode);
    return astNode;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}
