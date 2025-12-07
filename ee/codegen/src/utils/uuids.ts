import { createHash } from "crypto";

/**
 * Generate a deterministic UUID v4 from a string input using SHA-256 hashing.
 * This matches the Python implementation in src/vellum/workflows/utils/uuids.py
 *
 * @param inputStr - The string to hash
 * @returns A UUID v4 string derived from the hash
 */
export function uuid4FromHash(inputStr: string): string {
  // Create a SHA-256 hash of the input string
  const hashBytes = createHash("sha256").update(inputStr).digest();

  // Convert first 16 bytes into a mutable array
  // SHA-256 always produces 32 bytes, so we're guaranteed to have at least 16 bytes
  const hashList: number[] = Array.from(hashBytes.subarray(0, 16));

  // Set the version to 4 (UUID4)
  // Version bits (4 bits) should be set to 4
  const byte6 = hashList[6];
  const byte8 = hashList[8];
  if (byte6 !== undefined && byte8 !== undefined) {
    hashList[6] = (byte6 & 0x0f) | 0x40;
    // Set the variant to 0b10xxxxxx
    hashList[8] = (byte8 & 0x3f) | 0x80;
  }

  // Convert to UUID string format (8-4-4-4-12)
  const hex = hashList.map((b) => b.toString(16).padStart(2, "0")).join("");
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(
    12,
    16
  )}-${hex.slice(16, 20)}-${hex.slice(20, 32)}`;
}

/**
 * Generate a deterministic node ID from a module path and class name.
 * This matches the Python SDK's node ID generation pattern:
 * uuid4_from_hash(f"{node_class.__module__}.{node_class.__qualname__}")
 *
 * @param modulePath - The module path as an array of strings
 * @param className - The class name
 * @returns A UUID v4 string
 */
export function getNodeIdFromModuleAndName(
  modulePath: readonly string[],
  className: string
): string {
  const moduleStr = modulePath.join(".");
  return uuid4FromHash(`${moduleStr}.${className}`);
}
