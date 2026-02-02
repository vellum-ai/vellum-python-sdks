import { isNil } from "lodash";
import {
  ChatMessageRequest,
  FunctionCall,
  SearchResult,
  StringVellumValue as StringVellumValueType,
  VellumAudio,
  VellumDocument,
  VellumError,
  VellumImage,
  VellumValue as VellumVariableValueType,
  VellumVideo,
} from "vellum-ai/api";

import { ChatMessageContent } from "./chat-message-content";
import { ValueGenerationError } from "./errors";

import { VELLUM_CLIENT_MODULE_PATH } from "src/constants";
import { AccessAttribute } from "src/generators/extensions/access-attribute";
import { AstNode } from "src/generators/extensions/ast-node";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { FloatInstantiation } from "src/generators/extensions/float-instantiation";
import { ListInstantiation } from "src/generators/extensions/list-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { NoneInstantiation } from "src/generators/extensions/none-instantiation";
import { Reference } from "src/generators/extensions/reference";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { Writer } from "src/generators/extensions/writer";
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
    return new StrInstantiation(removeEscapeCharacters(value));
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
    return new FloatInstantiation(value);
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}

class JsonVellumValue extends AstNode {
  private astNode: AstNode;

  public constructor(value: unknown, schema?: Record<string, unknown>) {
    super();
    this.astNode = this.generateAstNode(value, schema);
  }

  private generateAstNode(
    value: unknown,
    schema?: Record<string, unknown>
  ): AstNode {
    const astNode = new Json(value, schema);
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
        new MethodArgument({
          name: "role",
          value: new StrInstantiation(chatMessage.role),
        }),
      ];

      if (chatMessage.text !== undefined && chatMessage.text !== null) {
        arguments_.push(
          new MethodArgument({
            name: "text",
            value: new StrInstantiation(
              removeEscapeCharacters(chatMessage.text)
            ),
          })
        );
      }

      if (chatMessage.source !== undefined && chatMessage.source !== null) {
        arguments_.push(
          new MethodArgument({
            name: "source",
            value: new StrInstantiation(chatMessage.source),
          })
        );
      }

      if (!isNil(chatMessage.content)) {
        const content = new ChatMessageContent({
          chatMessageContent: chatMessage.content,
          isRequestType,
        });

        arguments_.push(
          new MethodArgument({
            name: "content",
            value: content,
          })
        );
      }

      return new ClassInstantiation({
        classReference: new Reference({
          name: "ChatMessage" + (isRequestType ? "Request" : ""),
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        }),
        arguments_: arguments_,
      });
    });

    const astNode = new ListInstantiation(chatMessages, {
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
    const astNode = new ClassInstantiation({
      classReference: new Reference({
        name: "VellumError",
        modulePath: VELLUM_CLIENT_MODULE_PATH,
      }),
      arguments_: [
        new MethodArgument({
          name: "message",
          value: new StrInstantiation(message),
        }),
        new MethodArgument({
          name: "code",
          value: new StrInstantiation(code),
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
  private astNode: AstNode;

  public constructor(value: VellumAudio) {
    super();
    this.astNode = this.generateAstNode(value);
  }

  private generateAstNode(value: VellumAudio): AstNode {
    const arguments_ = [
      new MethodArgument({
        name: "src",
        value: new StrInstantiation(value.src),
      }),
    ];

    if (!isNil(value.metadata)) {
      arguments_.push(
        new MethodArgument({
          name: "metadata",
          value: new Json(value.metadata),
        })
      );
    }

    const astNode = new ClassInstantiation({
      classReference: new Reference({
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
  private astNode: AstNode;

  public constructor(value: VellumVideo) {
    super();
    this.astNode = this.generateAstNode(value);
  }

  private generateAstNode(value: VellumVideo): AstNode {
    const arguments_ = [
      new MethodArgument({
        name: "src",
        value: new StrInstantiation(value.src),
      }),
    ];

    if (!isNil(value.metadata)) {
      arguments_.push(
        new MethodArgument({
          name: "metadata",
          value: new Json(value.metadata),
        })
      );
    }

    const astNode = new ClassInstantiation({
      classReference: new Reference({
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
      new MethodArgument({
        name: "src",
        value: new StrInstantiation(value.src),
      }),
    ];

    if (!isNil(value.metadata)) {
      arguments_.push(
        new MethodArgument({
          name: "metadata",
          value: new Json(value.metadata),
        })
      );
    }

    const astNode = new ClassInstantiation({
      classReference: new Reference({
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
  private astNode: AstNode;

  public constructor(value: VellumDocument) {
    super();
    this.astNode = this.generateAstNode(value);
  }

  private generateAstNode(value: VellumDocument): AstNode {
    const arguments_ = [
      new MethodArgument({
        name: "src",
        value: new StrInstantiation(value.src),
      }),
    ];

    if (!isNil(value.metadata)) {
      arguments_.push(
        new MethodArgument({
          name: "metadata",
          value: new Json(value.metadata),
        })
      );
    }

    const astNode = new ClassInstantiation({
      classReference: new Reference({
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
  private astNode: AstNode;

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

    const astNode = new ListInstantiation(
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
  private astNode: AstNode;

  public constructor(value: FunctionCall) {
    super();
    this.astNode = this.generateAstNode(value);
  }

  private generateAstNode(value: FunctionCall): AstNode {
    const arguments_ = [
      new MethodArgument({
        name: "arguments",
        value: new Json(value.arguments),
      }),
      new MethodArgument({
        name: "name",
        value: new StrInstantiation(value.name),
      }),
    ];

    if (!isNil(value.id)) {
      arguments_.push(
        new MethodArgument({
          name: "id",
          value: new StrInstantiation(value.id),
        })
      );
    }

    const astNode = new ClassInstantiation({
      classReference: new Reference({
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
        new MethodArgument({
          name: "text",
          value: new StrInstantiation(result.text),
        }),
        new MethodArgument({
          name: "score",
          value: new FloatInstantiation(result.score),
        }),
        new MethodArgument({
          name: "keywords",
          value: new ListInstantiation(
            result.keywords.map((k) => new StrInstantiation(k))
          ),
        }),
        new MethodArgument({
          name: "document",
          value: (() => {
            const document = new ClassInstantiation({
              classReference: new Reference({
                name: "Document",
                modulePath: VELLUM_CLIENT_MODULE_PATH,
              }),
              arguments_: [
                new MethodArgument({
                  name: "id",
                  value: new StrInstantiation(result.document.id ?? ""),
                }),
                new MethodArgument({
                  name: "label",
                  value: new StrInstantiation(result.document.label ?? ""),
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
          new MethodArgument({
            name: "meta",
            value: new Json(result.meta),
          })
        );
      }

      return new ClassInstantiation({
        classReference: new Reference({
          name: "SearchResult",
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        }),
        arguments_: arguments_,
      });
    });

    const searchResults = new ListInstantiation(searchResultItems, {
      endWithComma: true,
    });

    this.inheritReferences(searchResults);

    return searchResults;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}

class ThinkingVellumValue extends AstNode {
  private astNode: AstNode;

  public constructor(value: StringVellumValueType) {
    super();
    this.astNode = this.generateAstNode(value);
  }

  private generateAstNode(value: StringVellumValueType): AstNode {
    const arguments_ = [
      new MethodArgument({
        name: "value",
        value: new StringVellumValue(value.value ?? ""),
      }),
    ];

    const astNode = new ClassInstantiation({
      classReference: new Reference({
        name: "StringVellumValue",
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
          this.astNode = new AccessAttribute({
            lhs: attributeConfig.lhs,
            rhs: new Reference({
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
        this.astNode = new JsonVellumValue(vellumValue.value, attributeConfig?.schema);
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
      case "VIDEO":
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
      case "THINKING":
        this.astNode = new ThinkingVellumValue(vellumValue.value);
        break;
      default:
        assertUnreachable(vellumValue);
    }

    this.inheritReferences(this.astNode);
  }

  public write(writer: Writer): void {
    if (this.astNode === null) {
      new NoneInstantiation().write(writer);
      return;
    }
    this.astNode.write(writer);
  }
}
