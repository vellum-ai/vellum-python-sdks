import { python } from "@fern-api/python-ast";
import { MethodArgument } from "@fern-api/python-ast/MethodArgument";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";
import { isNil } from "lodash";
import {
  ChatMessageContentRequest as ChatMessageContentRequestType,
  ChatMessageContent as ChatMessageContentType,
} from "vellum-ai/api";

import { VELLUM_CLIENT_MODULE_PATH } from "src/constants";
import { Json } from "src/generators/json";
import { assertUnreachable } from "src/utils/typing";

export namespace ChatMessageContent {
  export interface Args {
    chatMessageContent: ChatMessageContentRequestType | ChatMessageContentType;
    isRequestType?: boolean;
  }
}

export class ChatMessageContent extends AstNode {
  private chatMessageContent:
    | ChatMessageContentRequestType
    | ChatMessageContentType;
  private isRequestType: boolean;

  public constructor({
    chatMessageContent,
    isRequestType = true,
  }: ChatMessageContent.Args) {
    super();
    this.chatMessageContent = chatMessageContent;
    this.isRequestType = isRequestType;
    this.addReferences();
  }

  private addReferences(): void {
    if (this.chatMessageContent.type === "STRING") {
      this.addReference(this.getStringChatMessageContentRef());
    } else if (this.chatMessageContent.type === "FUNCTION_CALL") {
      this.addReference(this.getFunctionCallChatMessageContentRef());
      this.addReference(this.getFunctionCallChatMessageContentValueRef());
    } else if (this.chatMessageContent.type === "ARRAY") {
      this.addReference(this.getArrayChatMessageContentRef());
    } else if (this.chatMessageContent.type === "IMAGE") {
      this.addReference(this.getImageChatMessageContentRef());
    } else if (this.chatMessageContent.type === "AUDIO") {
      this.addReference(this.getAudioChatMessageContentRef());
    }
  }

  private getArrayChatMessageContentRef(): python.Reference {
    return python.reference({
      name: "ArrayChatMessageContent" + (this.isRequestType ? "Request" : ""),
      modulePath: VELLUM_CLIENT_MODULE_PATH,
    });
  }

  private getStringChatMessageContentRef(): python.Reference {
    return python.reference({
      name: "StringChatMessageContent" + (this.isRequestType ? "Request" : ""),
      modulePath: VELLUM_CLIENT_MODULE_PATH,
    });
  }

  private getFunctionCallChatMessageContentRef(): python.Reference {
    return python.reference({
      name:
        "FunctionCallChatMessageContent" +
        (this.isRequestType ? "Request" : ""),
      modulePath: VELLUM_CLIENT_MODULE_PATH,
    });
  }

  private getFunctionCallChatMessageContentValueRef(): python.Reference {
    return python.reference({
      name:
        "FunctionCallChatMessageContentValue" +
        (this.isRequestType ? "Request" : ""),
      modulePath: VELLUM_CLIENT_MODULE_PATH,
    });
  }

  private getAudioChatMessageContentRef(): python.Reference {
    return python.reference({
      name: "AudioChatMessageContent" + (this.isRequestType ? "Request" : ""),
      modulePath: VELLUM_CLIENT_MODULE_PATH,
    });
  }

  private getImageChatMessageContentRef(): python.Reference {
    return python.reference({
      name: "ImageChatMessageContent" + (this.isRequestType ? "Request" : ""),
      modulePath: VELLUM_CLIENT_MODULE_PATH,
    });
  }

  public write(writer: Writer): void {
    const contentType = this.chatMessageContent.type;

    if (contentType === "STRING") {
      const stringContentValue = this.chatMessageContent.value;

      const stringChatMessageContentRequestRef =
        this.getStringChatMessageContentRef();
      stringChatMessageContentRequestRef.write(writer);
      writer.write(`(value="${stringContentValue}")`);
      return;
    }

    if (contentType === "FUNCTION_CALL") {
      const functionCallChatMessageContentValue = this.chatMessageContent.value;

      const functionCallChatMessageContentValueArgs: MethodArgument[] = [];

      if (functionCallChatMessageContentValue.id !== undefined) {
        functionCallChatMessageContentValueArgs.push(
          new MethodArgument({
            name: "id",
            value: python.TypeInstantiation.str(
              functionCallChatMessageContentValue.id
            ),
          })
        );
      }

      functionCallChatMessageContentValueArgs.push(
        new MethodArgument({
          name: "name",
          value: python.TypeInstantiation.str(
            functionCallChatMessageContentValue.name
          ),
        })
      );

      if (functionCallChatMessageContentValue.arguments !== undefined) {
        functionCallChatMessageContentValueArgs.push(
          new MethodArgument({
            name: "arguments",
            value: new Json(functionCallChatMessageContentValue.arguments),
          })
        );
      }

      const functionCallChatMessageContentValueRequestRef =
        this.getFunctionCallChatMessageContentValueRef();

      const functionCallChatMessageContentValueInstance =
        python.instantiateClass({
          classReference: functionCallChatMessageContentValueRequestRef,
          arguments_: functionCallChatMessageContentValueArgs,
        });

      const functionCallChatMessageContentRequestRef =
        this.getFunctionCallChatMessageContentRef();

      const functionCallChatMessageContentRequestInstance =
        python.instantiateClass({
          classReference: functionCallChatMessageContentRequestRef,
          arguments_: [
            new MethodArgument({
              name: "value",
              value: functionCallChatMessageContentValueInstance,
            }),
          ],
        });

      functionCallChatMessageContentRequestInstance.write(writer);
      return;
    }

    if (contentType === "ARRAY") {
      const arrayValue = this.chatMessageContent.value;
      const arrayElements = arrayValue.map(
        (element) =>
          new ChatMessageContent({
            chatMessageContent: element as ChatMessageContentRequestType,
          })
      );
      const instance = python.instantiateClass({
        classReference: this.getArrayChatMessageContentRef(),
        arguments_: [
          python.methodArgument({
            name: "value",
            value: python.TypeInstantiation.list(arrayElements, {
              endWithComma: true,
            }),
          }),
        ],
      });
      this.inheritReferences(instance);
      instance.write(writer);
      return;
    }

    if (contentType === "IMAGE") {
      const imageContentValue = this.chatMessageContent.value;

      const imageChatMessageContentRequestRef =
        this.getImageChatMessageContentRef();

      const arguments_ = [
        python.methodArgument({
          name: "src",
          value: python.TypeInstantiation.str(imageContentValue.src),
        }),
      ];

      if (!isNil(imageContentValue.metadata)) {
        const metadataJson = new Json(imageContentValue.metadata);
        arguments_.push(
          python.methodArgument({
            name: "metadata",
            value: metadataJson,
          })
        );
      }

      const instance = python.instantiateClass({
        classReference: imageChatMessageContentRequestRef,
        arguments_: arguments_,
      });
      this.inheritReferences(instance);
      instance.write(writer);
      return;
    }

    if (contentType === "AUDIO") {
      const audioContentValue = this.chatMessageContent.value;

      const audioChatMessageContentRequestRef =
        this.getAudioChatMessageContentRef();

      const arguments_ = [
        python.methodArgument({
          name: "src",
          value: python.TypeInstantiation.str(audioContentValue.src),
        }),
      ];

      if (!isNil(audioContentValue.metadata)) {
        const metadataJson = new Json(audioContentValue.metadata);
        arguments_.push(
          python.methodArgument({
            name: "metadata",
            value: metadataJson,
          })
        );
      }

      const instance = python.instantiateClass({
        classReference: audioChatMessageContentRequestRef,
        arguments_: arguments_,
      });
      this.inheritReferences(instance);
      instance.write(writer);
      return;
    }

    assertUnreachable(contentType);
  }
}
