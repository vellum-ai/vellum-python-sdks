import { python } from "@fern-api/python-ast";
import * as Vellum from "vellum-ai/api";

import { VELLUM_CLIENT_MODULE_PATH } from "src/constants";
import { PythonType, UnionType } from "src/generators/extensions";
import { BuiltinListType } from "src/generators/extensions/list";
import { assertUnreachable } from "src/utils/typing";

/**
 * Converts a JSON Schema to a Python type annotation.
 * Currently supports basic types: string, number, integer, boolean, array, object, null.
 */
export function jsonSchemaToType(
  schema: Record<string, unknown>
): python.Type | PythonType {
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
      // Handle $ref in items
      if (items.$ref && typeof items.$ref === "string") {
        const refPath = items.$ref as string;
        // Extract the type name from the $ref path
        // e.g., "#/$defs/vellum.client.types.chat_message.ChatMessage" -> "ChatMessage"
        const typeName = refPath.split(".").pop() || refPath.split("/").pop();
        if (typeName) {
          const itemType = python.Type.reference(
            python.reference({
              name: typeName,
              modulePath: VELLUM_CLIENT_MODULE_PATH,
            })
          );
          return new BuiltinListType(itemType);
        }
      }
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
