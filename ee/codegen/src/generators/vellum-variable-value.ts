import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";
import { isNil } from "lodash";
import {
  ChatMessageRequest,
  FunctionCall,
  SearchResult,
  VellumAudio,
  VellumError,
  VellumImage,
  VellumValue as VellumVariableValueType,
} from "vellum-ai/api";

import { ChatMessageContent } from "./chat-message-content";

import { VELLUM_CLIENT_MODULE_PATH } from "src/constants";
import { Json } from "src/generators/json";
import { assertUnreachable } from "src/utils/typing";

class StringVellumValue extends AstNode {
  private value: string;

  public constructor(value: string) {
    super();
    this.value = value;
  }

  public write(writer: Writer): void {
    python.TypeInstantiation.str(this.value).write(writer);
  }
}

class NumberVellumValue extends AstNode {
  private value: number;

  public constructor(value: number) {
    super();
    this.value = value;
  }

  public write(writer: Writer): void {
    python.TypeInstantiation.float(this.value).write(writer);
  }
}

class JsonVellumValue extends AstNode {
  private astNode: Json;

  public constructor(value: unknown) {
    super();
    this.astNode = new Json(value);
    this.inheritReferences(this.astNode);
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}

class ChatHistoryVellumValue extends AstNode {
  private value: ChatMessageRequest[];
  private isRequestType: boolean;
  private contentsByIndex: Map<number, ChatMessageContent>;

  public constructor({
    value,
    isRequestType = true,
  }: {
    value: ChatMessageRequest[];
    isRequestType?: boolean;
  }) {
    super();
    this.value = value;
    this.isRequestType = isRequestType;
    this.contentsByIndex = new Map();

    this.setContentsByIndex();
  }

  private setContentsByIndex(): void {
    this.value.forEach((chatMessage, index) => {
      if (chatMessage.content !== undefined) {
        const content = new ChatMessageContent({
          chatMessageContent: chatMessage.content,
          isRequestType: this.isRequestType,
        });

        this.inheritReferences(content);

        this.contentsByIndex.set(index, content);
      }
    });
  }

  public write(writer: Writer): void {
    const chatHistoryValue = this.value;

    const chatMessages = chatHistoryValue.map((chatMessage, index) => {
      const arguments_ = [
        python.methodArgument({
          name: "role",
          value: python.TypeInstantiation.str(chatMessage.role),
        }),
      ];

      if (chatMessage.text !== undefined) {
        arguments_.push(
          python.methodArgument({
            name: "text",
            value: python.TypeInstantiation.str(chatMessage.text),
          })
        );
      }

      if (chatMessage.source !== undefined && chatMessage.source !== null) {
        arguments_.push(
          python.methodArgument({
            name: "source",
            value: python.TypeInstantiation.str(chatMessage.source),
          })
        );
      }

      if (chatMessage.content !== undefined) {
        const content = this.contentsByIndex.get(index);
        if (content === undefined) {
          throw new Error("Content not found");
        }

        arguments_.push(
          python.methodArgument({
            name: "content",
            value: content,
          })
        );
      }

      return python.instantiateClass({
        classReference: python.reference({
          name: "ChatMessage" + (this.isRequestType ? "Request" : ""),
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        }),
        arguments_: arguments_,
      });
    });

    python.TypeInstantiation.list(chatMessages).write(writer);
  }
}

class ErrorVellumValue extends AstNode {
  private astNode: AstNode;

  public constructor(value: VellumError) {
    super();
    this.astNode = this.generateVellumError(value);
  }

  private generateVellumError({ message, code }: VellumError) {
    const vellumErrorClass = python.instantiateClass({
      classReference: python.reference({
        name: "VellumError",
        modulePath: VELLUM_CLIENT_MODULE_PATH,
      }),
      arguments_: [
        python.methodArgument({
          name: "message",
          value: python.TypeInstantiation.str(message),
        }),
        python.methodArgument({
          name: "code",
          value: python.TypeInstantiation.str(code),
        }),
      ],
    });
    this.inheritReferences(vellumErrorClass);
    return vellumErrorClass;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}

class ImageVellumValue extends AstNode {
  private value: VellumImage;

  public constructor(value: VellumImage) {
    super();
    this.value = value;
  }

  public write(writer: Writer): void {
    const arguments_ = [
      python.methodArgument({
        name: "src",
        value: python.TypeInstantiation.str(this.value.src),
      }),
    ];

    if (!isNil(this.value.metadata)) {
      arguments_.push(
        python.methodArgument({
          name: "metadata",
          value: new Json(this.value.metadata),
        })
      );
    }

    python
      .instantiateClass({
        classReference: python.reference({
          name: "VellumImage",
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        }),
        arguments_: arguments_,
      })
      .write(writer);
  }
}

class ArrayVellumValue extends AstNode {
  private astNode: python.AstNode;

  public constructor(value: unknown) {
    super();
    if (!Array.isArray(value)) {
      throw new Error("Expected array value for ArrayVellumValue");
    }
    this.astNode = python.TypeInstantiation.list(
      value.map((item) => new VellumValue({ vellumValue: item }))
    );
    this.inheritReferences(this.astNode);
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}

class AudioVellumValue extends AstNode {
  private value: VellumAudio;

  public constructor(value: VellumAudio) {
    super();
    this.value = value;
  }

  public write(writer: Writer): void {
    const arguments_ = [
      python.methodArgument({
        name: "src",
        value: python.TypeInstantiation.str(this.value.src),
      }),
    ];

    if (!isNil(this.value.metadata)) {
      arguments_.push(
        python.methodArgument({
          name: "metadata",
          value: new Json(this.value.metadata),
        })
      );
    }

    python
      .instantiateClass({
        classReference: python.reference({
          name: "VellumAudio",
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        }),
        arguments_: arguments_,
      })
      .write(writer);
  }
}

class FunctionCallVellumValue extends AstNode {
  private value: FunctionCall;

  public constructor(value: FunctionCall) {
    super();
    this.value = value;
    this.inheritReferences(new Json(this.value.arguments));
  }

  public write(writer: Writer): void {
    const arguments_ = [
      python.methodArgument({
        name: "arguments",
        value: new Json(this.value.arguments),
      }),
      python.methodArgument({
        name: "name",
        value: python.TypeInstantiation.str(this.value.name),
      }),
    ];

    if (!isNil(this.value.id)) {
      arguments_.push(
        python.methodArgument({
          name: "id",
          value: python.TypeInstantiation.str(this.value.id),
        })
      );
    }

    python
      .instantiateClass({
        classReference: python.reference({
          name: "FunctionCall",
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        }),
        arguments_: arguments_,
      })
      .write(writer);
  }
}

class SearchResultsVellumValue extends AstNode {
  private astNode: AstNode;

  public constructor(value: SearchResult[]) {
    super();
    this.astNode = this.generateAstNode(value);
  }

  private generateAstNode(value: SearchResult[]): AstNode {
    const searchResultItems = value.map((result) => {
      const arguments_ = [
        python.methodArgument({
          name: "text",
          value: python.TypeInstantiation.str(result.text),
        }),
        python.methodArgument({
          name: "score",
          value: python.TypeInstantiation.float(result.score),
        }),
        python.methodArgument({
          name: "keywords",
          value: python.TypeInstantiation.list(
            result.keywords.map((k) => python.TypeInstantiation.str(k))
          ),
        }),
        python.methodArgument({
          name: "document",
          value: (() => {
            const document = python.instantiateClass({
              classReference: python.reference({
                name: "Document",
                modulePath: VELLUM_CLIENT_MODULE_PATH,
              }),
              arguments_: [
                python.methodArgument({
                  name: "id",
                  value: python.TypeInstantiation.str(result.document.id ?? ""),
                }),
                python.methodArgument({
                  name: "label",
                  value: python.TypeInstantiation.str(
                    result.document.label ?? ""
                  ),
                }),
              ],
            });
            this.inheritReferences(document);
            return document;
          })(),
        }),
      ];

      if (result.meta) {
        arguments_.push(
          python.methodArgument({
            name: "meta",
            value: new Json(result.meta),
          })
        );
      }

      return python.instantiateClass({
        classReference: python.reference({
          name: "SearchResult",
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        }),
        arguments_: arguments_,
      });
    });

    const searchResults = python.TypeInstantiation.list(searchResultItems);

    this.inheritReferences(searchResults);

    return searchResults;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}

export namespace VellumValue {
  export type Args = {
    vellumValue: VellumVariableValueType;
    isRequestType?: boolean;
  };
}

export class VellumValue extends AstNode {
  private astNode: AstNode | null;

  public constructor({ vellumValue, isRequestType }: VellumValue.Args) {
    super();
    this.astNode = null;

    if (vellumValue.value === undefined) {
      return;
    }
    switch (vellumValue.type) {
      case "STRING":
        this.astNode = new StringVellumValue(vellumValue.value);
        break;
      case "NUMBER":
        this.astNode = new NumberVellumValue(vellumValue.value);
        break;
      case "JSON":
        this.astNode = new JsonVellumValue(vellumValue.value);
        break;
      case "CHAT_HISTORY":
        this.astNode = new ChatHistoryVellumValue({
          value: vellumValue.value,
          isRequestType,
        });
        break;
      case "ERROR":
        this.astNode = new ErrorVellumValue(vellumValue.value);
        break;
      case "IMAGE":
        this.astNode = new ImageVellumValue(vellumValue.value);
        break;
      case "ARRAY":
        this.astNode = new ArrayVellumValue(vellumValue.value);
        break;
      case "AUDIO":
        this.astNode = new AudioVellumValue(vellumValue.value);
        break;
      case "SEARCH_RESULTS":
        this.astNode = new SearchResultsVellumValue(vellumValue.value);
        break;
      case "FUNCTION_CALL":
        this.astNode = new FunctionCallVellumValue(vellumValue.value);
        break;
      default:
        assertUnreachable(vellumValue);
    }

    this.inheritReferences(this.astNode);
  }

  public write(writer: Writer): void {
    if (this.astNode === null) {
      writer.write("None");
      return;
    }

    this.astNode.write(writer);
  }
}
