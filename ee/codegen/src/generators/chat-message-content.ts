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
  private astNode: AstNode;

  public constructor({
    chatMessageContent,
    isRequestType = true,
  }: ChatMessageContent.Args) {
    super();
    this.astNode = this.generateAstNode(chatMessageContent, isRequestType);
  }

  private generateAstNode(
    chatMessageContent: ChatMessageContentRequestType | ChatMessageContentType,
    isRequestType: boolean
  ): AstNode {
    const contentType = chatMessageContent.type;

    let astNode: AstNode;

    if (contentType === "STRING") {
      const stringContentValue = chatMessageContent.value;

      astNode = python.instantiateClass({
        classReference: python.reference({
          name: "StringChatMessageContent" + (isRequestType ? "Request" : ""),
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        }),
        arguments_: [
          python.methodArgument({
            name: "value",
            value: python.TypeInstantiation.str(stringContentValue),
          }),
        ],
      });
    } else if (contentType === "FUNCTION_CALL") {
      const functionCallChatMessageContentValue = chatMessageContent.value;

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

      const functionCallChatMessageContentValueRequestRef = python.reference({
        name:
          "FunctionCallChatMessageContentValue" +
          (isRequestType ? "Request" : ""),
        modulePath: VELLUM_CLIENT_MODULE_PATH,
      });

      const functionCallChatMessageContentValueInstance =
        python.instantiateClass({
          classReference: functionCallChatMessageContentValueRequestRef,
          arguments_: functionCallChatMessageContentValueArgs,
        });

      astNode = python.instantiateClass({
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
    } else if (contentType === "ARRAY") {
      const arrayValue = chatMessageContent.value;
      const arrayElements = arrayValue.map(
        (element) =>
          new ChatMessageContent({
            chatMessageContent: element as ChatMessageContentRequestType,
          })
      );
      astNode = python.instantiateClass({
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
    } else if (contentType === "IMAGE") {
      const imageContentValue = chatMessageContent.value;

      const imageChatMessageContentRequestRef = python.reference({
        name: "ImageChatMessageContent" + (isRequestType ? "Request" : ""),
        modulePath: VELLUM_CLIENT_MODULE_PATH,
      });

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

      astNode = python.instantiateClass({
        classReference: imageChatMessageContentRequestRef,
        arguments_: arguments_,
      });
    } else if (contentType === "AUDIO") {
      const audioContentValue = chatMessageContent.value;

      const audioChatMessageContentRequestRef = python.reference({
        name: "AudioChatMessageContent" + (isRequestType ? "Request" : ""),
        modulePath: VELLUM_CLIENT_MODULE_PATH,
      });

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

      astNode = python.instantiateClass({
        classReference: audioChatMessageContentRequestRef,
        arguments_: arguments_,
      });
    } else {
      assertUnreachable(contentType);
    }

    this.inheritReferences(astNode);

    return astNode;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}
