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
  VellumDocument as VellumDocumentType,
  VellumDocumentRequest as VellumDocumentRequestType,
  // VellumVideo as VellumVideoType,
  // VellumVideoRequest as VellumVideoRequestType,
} from "vellum-ai/api";

import { VELLUM_CLIENT_MODULE_PATH } from "src/constants";
import { Json } from "src/generators/json";
import { removeEscapeCharacters } from "src/utils/casing";
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
          value: python.TypeInstantiation.str(removeEscapeCharacters(value)),
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

    if (!isNil(value.id)) {
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

    const audioArgs = [
      python.methodArgument({
        name: "src",
        value: python.TypeInstantiation.str(value.src),
      }),
    ];

    if (!isNil(value.metadata)) {
      const metadataJson = new Json(value.metadata);
      audioArgs.push(
        python.methodArgument({
          name: "metadata",
          value: metadataJson,
        })
      );
    }

    const arguments_ = [
      python.methodArgument({
        name: "value",
        value: python.instantiateClass({
          classReference: python.reference({
            name: "VellumAudio" + (isRequestType ? "Request" : ""),
            modulePath: VELLUM_CLIENT_MODULE_PATH,
          }),
          arguments_: audioArgs,
        }),
      }),
    ];

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

class VideoChatMessageContent extends AstNode {
  private astNode: AstNode;

  public constructor(
    value: unknown, // VellumVideoType | VellumVideoRequestType,
    isRequestType: boolean
  ) {
    super();
    this.astNode = this.generateAstNode(value, isRequestType);
  }

  private generateAstNode(
    value: unknown, // VellumVideoType | VellumVideoRequestType,
    isRequestType: boolean
  ): AstNode {
    const videoChatMessageContentRequestRef = python.reference({
      name: "VideoChatMessageContent" + (isRequestType ? "Request" : ""),
      modulePath: VELLUM_CLIENT_MODULE_PATH,
    });

    const videoArgs = [
      python.methodArgument({
        name: "src",
        // @ts-ignore
        value: python.TypeInstantiation.str(value.src),
      }),
    ];

    // @ts-ignore
    if (!isNil(value.metadata)) {
      // @ts-ignore
      const metadataJson = new Json(value.metadata);
      videoArgs.push(
        python.methodArgument({
          name: "metadata",
          value: metadataJson,
        })
      );
    }

    const arguments_ = [
      python.methodArgument({
        name: "value",
        value: python.instantiateClass({
          classReference: python.reference({
            name: "VellumVideo" + (isRequestType ? "Request" : ""),
            modulePath: VELLUM_CLIENT_MODULE_PATH,
          }),
          arguments_: videoArgs,
        }),
      }),
    ];

    const astNode = python.instantiateClass({
      classReference: videoChatMessageContentRequestRef,
      arguments_: arguments_,
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

    const imageArgs = [
      python.methodArgument({
        name: "src",
        value: python.TypeInstantiation.str(value.src),
      }),
    ];

    if (!isNil(value.metadata)) {
      const metadataJson = new Json(value.metadata);
      imageArgs.push(
        python.methodArgument({
          name: "metadata",
          value: metadataJson,
        })
      );
    }

    const arguments_ = [
      python.methodArgument({
        name: "value",
        value: python.instantiateClass({
          classReference: python.reference({
            name: "VellumImage" + (isRequestType ? "Request" : ""),
            modulePath: VELLUM_CLIENT_MODULE_PATH,
          }),
          arguments_: imageArgs,
        }),
      }),
    ];

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

class DocumentChatMessageContent extends AstNode {
  private astNode: AstNode;

  public constructor(
    value: VellumDocumentType | VellumDocumentRequestType,
    isRequestType: boolean
  ) {
    super();
    this.astNode = this.generateAstNode(value, isRequestType);
  }

  private generateAstNode(
    value: VellumDocumentType | VellumDocumentRequestType,
    isRequestType: boolean
  ): AstNode {
    const documentChatMessageContentRequestRef = python.reference({
      name: "DocumentChatMessageContent" + (isRequestType ? "Request" : ""),
      modulePath: VELLUM_CLIENT_MODULE_PATH,
    });

    const documentArgs = [
      python.methodArgument({
        name: "src",
        value: python.TypeInstantiation.str(value.src),
      }),
    ];

    if (!isNil(value.metadata)) {
      const metadataJson = new Json(value.metadata);
      documentArgs.push(
        python.methodArgument({
          name: "metadata",
          value: metadataJson,
        })
      );
    }

    const arguments_ = [
      python.methodArgument({
        name: "value",
        value: python.instantiateClass({
          classReference: python.reference({
            name: "VellumDocument" + (isRequestType ? "Request" : ""),
            modulePath: VELLUM_CLIENT_MODULE_PATH,
          }),
          arguments_: documentArgs,
        }),
      }),
    ];

    const astNode = python.instantiateClass({
      classReference: documentChatMessageContentRequestRef,
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
      case "AUDIO": {
        astNode = new AudioChatMessageContent(
          chatMessageContent.value,
          isRequestType
        );
        break;
      }
      // @ts-expect-error
      case "VIDEO": {
        astNode = new VideoChatMessageContent(
          // @ts-expect-error
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
      case "DOCUMENT": {
        astNode = new DocumentChatMessageContent(
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
