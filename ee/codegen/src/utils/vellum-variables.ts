import * as Vellum from "vellum-ai/api";

import {
  TYPING_MODULE_PATH,
  VELLUM_CLIENT_MODULE_PATH,
  VELLUM_WORKFLOWS_ROOT_MODULE_PATH,
} from "src/constants";
import { PythonType, UnionType } from "src/generators/extensions";
import { AnyType } from "src/generators/extensions/any-type";
import { BoolType } from "src/generators/extensions/bool-type";
import { BuiltinDictType } from "src/generators/extensions/dict";
import { FloatType } from "src/generators/extensions/float-type";
import { IntType } from "src/generators/extensions/int-type";
import { BuiltinListType } from "src/generators/extensions/list";
import { NoneType } from "src/generators/extensions/none-type";
import { Reference } from "src/generators/extensions/reference";
import { StrType } from "src/generators/extensions/str-type";
import { TypeReference } from "src/generators/extensions/type-reference";
import { assertUnreachable } from "src/utils/typing";

/**
 * Parses a $ref path and extracts the type name and module path.
 * Examples:
 * - "#/$defs/vellum.client.types.chat_message.ChatMessage" -> { name: "ChatMessage", modulePath: ["vellum", "client", "types", "chat_message"] }
 * - "#/definitions/ChatMessage" -> { name: "ChatMessage", modulePath: ["vellum", "workflows"] }
 */
function parseRef(refPath: string): {
  name: string;
  modulePath: string[];
} {
  // Remove the leading "#/" or "#/$defs/" prefix
  const withoutPrefix = refPath.replace(/^#\/(\$defs\/)?/, "");

  // Split by "/" to get path segments
  const segments = withoutPrefix.split("/");

  // The last segment contains the full dotted path to the type
  const lastSegment = segments[segments.length - 1];

  // Handle case where lastSegment might be undefined (empty ref path)
  if (!lastSegment) {
    return { name: "Any", modulePath: [...TYPING_MODULE_PATH] };
  }

  // Split the last segment by "." to separate module path from type name
  const parts = lastSegment.split(".");

  if (parts.length > 1) {
    // Extract type name (last part) and module path (everything before)
    const name = parts[parts.length - 1];
    if (!name) {
      // Edge case: ref ends with a dot
      return { name: "Any", modulePath: [...TYPING_MODULE_PATH] };
    }
    const modulePath = parts.slice(0, -1);
    return { name, modulePath };
  } else {
    // No dots in the path, just a type name - use workflows root module path
    return {
      name: lastSegment,
      modulePath: [...VELLUM_WORKFLOWS_ROOT_MODULE_PATH],
    };
  }
}

/**
 * Converts a JSON Schema to a Python type annotation.
 * Currently supports basic types: string, number, integer, boolean, array, object, null, and $ref.
 */
export function jsonSchemaToType(schema: Record<string, unknown>): PythonType {
  // Handle $ref at the top level
  if (schema.$ref && typeof schema.$ref === "string") {
    const { name, modulePath } = parseRef(schema.$ref);
    return new TypeReference(
      new Reference({
        name,
        modulePath,
      })
    );
  }

  const schemaType = schema.type;

  if (schemaType === "string") {
    return new StrType();
  } else if (schemaType === "integer") {
    return new IntType();
  } else if (schemaType === "number") {
    return new FloatType();
  } else if (schemaType === "boolean") {
    return new BoolType();
  } else if (schemaType === "array") {
    const items = schema.items as Record<string, unknown> | undefined;
    if (items) {
      const itemType = jsonSchemaToType(items);
      return new BuiltinListType(itemType);
    }
    return new BuiltinListType(new AnyType());
  } else if (schemaType === "object") {
    // Handle additionalProperties for typed dict types
    const additionalProperties = schema.additionalProperties as
      | Record<string, unknown>
      | undefined;
    if (additionalProperties) {
      const valueType = jsonSchemaToType(additionalProperties);
      return new BuiltinDictType(new StrType(), valueType);
    }
    // Fallback to old behavior for plain objects
    return new BuiltinDictType(new StrType(), new AnyType());
  } else if (schemaType === "null") {
    return new NoneType();
  } else if ("anyOf" in schema && Array.isArray(schema.anyOf)) {
    return new UnionType(schema.anyOf.map(jsonSchemaToType));
  }

  return new AnyType();
}

export function getVellumVariablePrimitiveType(
  vellumVariableType: Vellum.VellumVariableType
): PythonType {
  switch (vellumVariableType) {
    case "STRING":
      return new StrType();
    case "NUMBER":
      return new UnionType([new FloatType(), new IntType()]);
    case "JSON":
      return new AnyType();
    case "CHAT_HISTORY":
      return new BuiltinListType(
        new TypeReference(
          new Reference({
            name: "ChatMessage",
            modulePath: VELLUM_CLIENT_MODULE_PATH,
          })
        )
      );
    case "SEARCH_RESULTS":
      return new BuiltinListType(
        new TypeReference(
          new Reference({
            name: "SearchResult",
            modulePath: VELLUM_CLIENT_MODULE_PATH,
          })
        )
      );
    case "ERROR":
      return new TypeReference(
        new Reference({
          name: "VellumError",
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        })
      );
    case "ARRAY":
      return new BuiltinListType(
        new TypeReference(
          new Reference({
            name: "VellumValue",
            modulePath: VELLUM_CLIENT_MODULE_PATH,
          })
        )
      );
    case "FUNCTION_CALL":
      return new TypeReference(
        new Reference({
          name: "FunctionCall",
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        })
      );
    case "AUDIO":
      return new TypeReference(
        new Reference({
          name: "VellumAudio",
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        })
      );
    case "VIDEO":
      return new TypeReference(
        new Reference({
          name: "VellumVideo",
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        })
      );
    case "IMAGE":
      return new TypeReference(
        new Reference({
          name: "VellumImage",
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        })
      );
    case "DOCUMENT":
      return new TypeReference(
        new Reference({
          name: "VellumDocument",
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        })
      );
    case "THINKING":
      return new TypeReference(
        new Reference({
          name: "StringVellumValue",
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        })
      );
    case "NULL":
      return new NoneType();
    default: {
      assertUnreachable(vellumVariableType);
    }
  }
}
