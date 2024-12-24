import { python } from "@fern-api/python-ast";
import { validate as uuidValidate } from "uuid";

export function generateId(id: string): python.TypeInstantiation {
  return uuidValidate(id)
    ? python.TypeInstantiation.uuid(id)
    : python.TypeInstantiation.str(id);
}
