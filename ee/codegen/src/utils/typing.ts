import { isNil } from "lodash";

import { ValueGenerationError } from "src/generators/errors";

export function isDefined<TValue>(value: TValue | undefined): value is TValue {
  return value !== undefined;
}

export function assertUnreachable(_: never): never {
  throw new ValueGenerationError("Didn't expect to get here");
}

export function isNilOrEmpty<T>(
  collection: T[] | Record<string, T> | null | undefined
): boolean {
  if (isNil(collection)) {
    return true;
  }

  if (Array.isArray(collection)) {
    return collection.length === 0;
  }

  if (typeof collection === "object") {
    return (
      Object.keys(collection).length === 0 ||
      Object.values(collection).every((value) => value === undefined)
    );
  }

  return false;
}
