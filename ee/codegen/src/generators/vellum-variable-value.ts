import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";
import { isNil } from "lodash";
import {
  ChatMessageRequest,
  FunctionCall,
  SearchResult,
  VellumAudio,
  VellumDocument,
  VellumError,
  VellumImage,
  VellumValue as VellumVariableValueType,
  // VellumVideo,
} from "vellum-ai/api";

import { ChatMessageContent } from "./chat-message-content";
import { ValueGenerationError } from "./errors";

import { VELLUM_CLIENT_MODULE_PATH } from "src/constants";
import { Json } from "src/generators/json";
import { AttributeConfig, IterableConfig } from "src/types/vellum";
import { removeEscapeCharacters } from "src/utils/casing";
import { assertUnreachable } from "src/utils/typing";

class StringVellumValue extends AstNode {
  private astNode: AstNode;

  public constructor(value: string) {
    super();
    this.astNode = this.generateAstNode(value);
  }

  private generateAstNode(value: string): AstNode {
    return python.TypeInstantiation.str(removeEscapeCharacters(value));
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}

class NumberVellumValue extends AstNode {
  private astNode: AstNode;

  public constructor(value: number) {
    super();
    this.astNode = this.generateAstNode(value);
  }

  private generateAstNode(value: number): AstNode {
    return python.TypeInstantiation.float(value);
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}

class JsonVellumValue extends AstNode {
  private astNode: AstNode;

  public constructor(value: unknown) {
    super();
    this.astNode = this.generateAstNode(value);
  }

  private generateAstNode(value: unknown): AstNode {
    const astNode = new Json(value);
    this.inheritReferences(astNode);
    return astNode;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}

class ChatHistoryVellumValue extends AstNode {
  private astNode: AstNode | undefined;

  public constructor({
    value,
    isRequestType = false,
  }: {
    value: ChatMessageRequest[];
    isRequestType?: boolean;
  }) {
    super();
    this.astNode = this.generateAstNode(value, isRequestType);
  }

  private generateAstNode(
    value: ChatMessageRequest[],
    isRequestType: boolean
  ): AstNode | undefined {
    if (isNil(value)) {
      return undefined;
    }
    const chatMessages = value.map((chatMessage) => {
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
            value: python.TypeInstantiation.str(
              removeEscapeCharacters(chatMessage.text)
            ),
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

      if (!isNil(chatMessage.content)) {
        const content = new ChatMessageContent({
          chatMessageContent: chatMessage.content,
          isRequestType,
        });

        arguments_.push(
          python.methodArgument({
            name: "content",
            value: content,
          })
        );
      }

      return python.instantiateClass({
        classReference: python.reference({
          name: "ChatMessage" + (isRequestType ? "Request" : ""),
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        }),
        arguments_: arguments_,
      });
    });

    const astNode = python.TypeInstantiation.list(chatMessages, {
      endWithComma: true,
    });
    this.inheritReferences(astNode);
    return astNode;
  }

  public write(writer: Writer): void {
    if (this.astNode) {
      this.astNode.write(writer);
    }
  }
}

class ErrorVellumValue extends AstNode {
  private astNode: AstNode;

  public constructor(value: VellumError) {
    super();
    this.astNode = this.generateAstNode(value);
  }

  private generateAstNode({ message, code }: VellumError) {
    const astNode = python.instantiateClass({
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
    this.inheritReferences(astNode);
    return astNode;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}

class AudioVellumValue extends AstNode {
  private astNode: python.AstNode;

  public constructor(value: VellumAudio) {
    super();
    this.astNode = this.generateAstNode(value);
  }

  private generateAstNode(value: VellumAudio): AstNode {
    const arguments_ = [
      python.methodArgument({
        name: "src",
        value: python.TypeInstantiation.str(value.src),
      }),
    ];

    if (!isNil(value.metadata)) {
      arguments_.push(
        python.methodArgument({
          name: "metadata",
          value: new Json(value.metadata),
        })
      );
    }

    const astNode = python.instantiateClass({
      classReference: python.reference({
        name: "VellumAudio",
        modulePath: VELLUM_CLIENT_MODULE_PATH,
      }),
      arguments_: arguments_,
    });

    this.inheritReferences(astNode);
    return astNode;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}

class VideoVellumValue extends AstNode {
  private astNode: python.AstNode;

  public constructor(value: unknown) {
    // VellumVideo) {
    super();
    this.astNode = this.generateAstNode(value);
  }

  private generateAstNode(value: unknown): AstNode {
    // VellumVideo): AstNode {
    const arguments_ = [
      python.methodArgument({
        name: "src",
        // @ts-ignore
        value: python.TypeInstantiation.str(value.src),
      }),
    ];

    // @ts-ignore
    if (!isNil(value.metadata)) {
      arguments_.push(
        python.methodArgument({
          name: "metadata",
          // @ts-ignore
          value: new Json(value.metadata),
        })
      );
    }

    const astNode = python.instantiateClass({
      classReference: python.reference({
        name: "VellumVideo",
        modulePath: VELLUM_CLIENT_MODULE_PATH,
      }),
      arguments_: arguments_,
    });

    this.inheritReferences(astNode);
    return astNode;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}

class ImageVellumValue extends AstNode {
  private astNode: AstNode;

  public constructor(value: VellumImage) {
    super();
    this.astNode = this.generateAstNode(value);
  }

  private generateAstNode(value: VellumImage): AstNode {
    const arguments_ = [
      python.methodArgument({
        name: "src",
        value: python.TypeInstantiation.str(value.src),
      }),
    ];

    if (!isNil(value.metadata)) {
      arguments_.push(
        python.methodArgument({
          name: "metadata",
          value: new Json(value.metadata),
        })
      );
    }

    const astNode = python.instantiateClass({
      classReference: python.reference({
        name: "VellumImage",
        modulePath: VELLUM_CLIENT_MODULE_PATH,
      }),
      arguments_: arguments_,
    });

    this.inheritReferences(astNode);

    return astNode;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}

class DocumentVellumValue extends AstNode {
  private astNode: python.AstNode;

  public constructor(value: VellumDocument) {
    super();
    this.astNode = this.generateAstNode(value);
  }

  private generateAstNode(value: VellumDocument): AstNode {
    const arguments_ = [
      python.methodArgument({
        name: "src",
        value: python.TypeInstantiation.str(value.src),
      }),
    ];

    if (!isNil(value.metadata)) {
      arguments_.push(
        python.methodArgument({
          name: "metadata",
          value: new Json(value.metadata),
        })
      );
    }

    const astNode = python.instantiateClass({
      classReference: python.reference({
        name: "VellumDocument",
        modulePath: VELLUM_CLIENT_MODULE_PATH,
      }),
      arguments_: arguments_,
    });

    this.inheritReferences(astNode);
    return astNode;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}

class ArrayVellumValue extends AstNode {
  private astNode: python.AstNode;

  public constructor(value: unknown, iterableConfig?: IterableConfig) {
    super();
    this.astNode = this.generateAstNode(value, iterableConfig);
  }

  private generateAstNode(
    value: unknown,
    iterableConfig?: IterableConfig
  ): AstNode {
    if (!Array.isArray(value)) {
      throw new ValueGenerationError(
        "Expected array value for ArrayVellumValue"
      );
    }

    const astNode = python.TypeInstantiation.list(
      value.map((item) => new VellumValue({ vellumValue: item })),
      iterableConfig ?? { endWithComma: true }
    );

    this.inheritReferences(astNode);
    return astNode;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}

class FunctionCallVellumValue extends AstNode {
  private astNode: python.AstNode;

  public constructor(value: FunctionCall) {
    super();
    this.astNode = this.generateAstNode(value);
  }

  private generateAstNode(value: FunctionCall): AstNode {
    const arguments_ = [
      python.methodArgument({
        name: "arguments",
        value: new Json(value.arguments),
      }),
      python.methodArgument({
        name: "name",
        value: python.TypeInstantiation.str(value.name),
      }),
    ];

    if (!isNil(value.id)) {
      arguments_.push(
        python.methodArgument({
          name: "id",
          value: python.TypeInstantiation.str(value.id),
        })
      );
    }

    const astNode = python.instantiateClass({
      classReference: python.reference({
        name: "FunctionCall",
        modulePath: VELLUM_CLIENT_MODULE_PATH,
      }),
      arguments_: arguments_,
    });

    this.inheritReferences(astNode);
    return astNode;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
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

    const searchResults = python.TypeInstantiation.list(searchResultItems, {
      endWithComma: true,
    });

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
    iterableConfig?: IterableConfig;
    attributeConfig?: AttributeConfig;
  };
}

export class VellumValue extends AstNode {
  private astNode: AstNode | null;

  public constructor({
    vellumValue,
    isRequestType,
    iterableConfig,
    attributeConfig,
  }: VellumValue.Args) {
    super();
    this.astNode = null;

    if (isNil(vellumValue.value)) {
      return;
    }
    switch (vellumValue.type) {
      case "STRING":
        this.astNode = new StringVellumValue(vellumValue.value);
        if (attributeConfig) {
          this.astNode = python.accessAttribute({
            lhs: attributeConfig.lhs,
            rhs: python.reference({
              name: vellumValue.value,
              modulePath: [],
            }),
          });
        }
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
      case "AUDIO":
        this.astNode = new AudioVellumValue(vellumValue.value);
        break;
      // @ts-expect-error
      case "VIDEO":
        // @ts-expect-error
        this.astNode = new VideoVellumValue(vellumValue.value);
        break;
      case "IMAGE":
        this.astNode = new ImageVellumValue(vellumValue.value);
        break;
      case "DOCUMENT":
        this.astNode = new DocumentVellumValue(vellumValue.value);
        break;
      case "ARRAY":
        this.astNode = new ArrayVellumValue(vellumValue.value, iterableConfig);
        break;
      case "SEARCH_RESULTS":
        this.astNode = new SearchResultsVellumValue(vellumValue.value);
        break;
      case "FUNCTION_CALL":
        this.astNode = new FunctionCallVellumValue(vellumValue.value);
        break;
      // TODO: Implement Document vellum variable type support
      // https://linear.app/vellum/issue/APO-189/add-codegen-support-for-new-document-variable-type
      default:
        assertUnreachable(vellumValue);
    }

    this.inheritReferences(this.astNode);
  }

  public write(writer: Writer): void {
    if (this.astNode === null) {
      python.TypeInstantiation.none().write(writer);
      return;
    }
    this.astNode.write(writer);
  }
}
