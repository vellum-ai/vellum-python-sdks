import { python } from "@fern-api/python-ast";
import * as Vellum from "vellum-ai/api";

import {
  TYPING_MODULE_PATH,
  VELLUM_CLIENT_MODULE_PATH,
  VELLUM_WORKFLOWS_ROOT_MODULE_PATH,
} from "src/constants";
import { PythonType, UnionType } from "src/generators/extensions";
import { BuiltinListType } from "src/generators/extensions/list";
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
export function jsonSchemaToType(
  schema: Record<string, unknown>
): python.Type | PythonType {
  // Handle $ref at the top level
  if (schema.$ref && typeof schema.$ref === "string") {
    const { name, modulePath } = parseRef(schema.$ref);
    return python.Type.reference(
      python.reference({
        name,
        modulePath,
      })
    );
  }

  const schemaType = schema.type;

  if (schemaType === "string") {
    return python.Type.str();
  } else if (schemaType === "integer") {
    return python.Type.int();
  } else if (schemaType === "number") {
    return python.Type.float();
  } else if (schemaType === "boolean") {
    return python.Type.bool();
  } else if (schemaType === "array") {
    const items = schema.items as Record<string, unknown> | undefined;
    if (items) {
      const itemType = jsonSchemaToType(items);
      return new BuiltinListType(itemType);
    }
    return new BuiltinListType(python.Type.any());
  } else if (schemaType === "object") {
    return python.Type.dict(python.Type.str(), python.Type.any());
  } else if (schemaType === "null") {
    return python.Type.none();
  } else if ("anyOf" in schema && Array.isArray(schema.anyOf)) {
    return new UnionType(schema.anyOf.map(jsonSchemaToType));
  }

  return python.Type.any();
}

export function getVellumVariablePrimitiveType(
  vellumVariableType: Vellum.VellumVariableType
): python.Type | PythonType {
  switch (vellumVariableType) {
    case "STRING":
      return python.Type.str();
    case "NUMBER":
      return python.Type.union([python.Type.float(), python.Type.int()]);
    case "JSON":
      return python.Type.any();
    case "CHAT_HISTORY":
      return new BuiltinListType(
        python.Type.reference(
          python.reference({
            name: "ChatMessage",
            modulePath: VELLUM_CLIENT_MODULE_PATH,
          })
        )
      );
    case "SEARCH_RESULTS":
      return new BuiltinListType(
        python.Type.reference(
          python.reference({
            name: "SearchResult",
            modulePath: VELLUM_CLIENT_MODULE_PATH,
          })
        )
      );
    case "ERROR":
      return python.Type.reference(
        python.reference({
          name: "VellumError",
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        })
      );
    case "ARRAY":
      return new BuiltinListType(
        python.Type.reference(
          python.reference({
            name: "VellumValue",
            modulePath: VELLUM_CLIENT_MODULE_PATH,
          })
        )
      );
    case "FUNCTION_CALL":
      return python.Type.reference(
        python.reference({
          name: "FunctionCall",
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        })
      );
    case "AUDIO":
      return python.Type.reference(
        python.reference({
          name: "VellumAudio",
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        })
      );
    case "VIDEO":
      return python.Type.reference(
        python.reference({
          name: "VellumVideo",
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        })
      );
    case "IMAGE":
      return python.Type.reference(
        python.reference({
          name: "VellumImage",
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        })
      );
    case "DOCUMENT":
      return python.Type.reference(
        python.reference({
          name: "VellumDocument",
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        })
      );
    case "THINKING":
      return python.Type.reference(
        python.reference({
          name: "StringVellumValue",
          modulePath: VELLUM_CLIENT_MODULE_PATH,
        })
      );
    case "NULL":
      return python.Type.none();
    default: {
      assertUnreachable(vellumVariableType);
    }
  }
}
