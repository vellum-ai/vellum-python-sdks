import { python } from "@fern-api/python-ast";
import * as Vellum from "vellum-ai/api";

import { VELLUM_CLIENT_MODULE_PATH } from "src/constants";
import { assertUnreachable } from "src/utils/typing";

export function getVellumVariablePrimitiveType(
  vellumVariableType: Vellum.VellumVariableType
): python.Type {
  switch (vellumVariableType) {
    case "STRING":
      return python.Type.str();
    case "NUMBER":
      return python.Type.union([python.Type.float(), python.Type.int()]);
    case "JSON":
      return python.Type.any();
    case "CHAT_HISTORY":
      return python.Type.list(
        python.Type.reference(
          python.reference({
            name: "ChatMessage",
            modulePath: VELLUM_CLIENT_MODULE_PATH,
          })
        )
      );
    case "SEARCH_RESULTS":
      return python.Type.list(
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
      return python.Type.list(
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
