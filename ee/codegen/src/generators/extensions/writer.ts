/**
 * Re-export Writer from @fern-api/python-ast/core/Writer
 * This centralizes the import path as part of the effort to eject from the python-ast package.
 *
 * All consumers should import Writer from this module instead of directly from @fern-api/python-ast.
 * This allows us to eventually replace the implementation without updating all import sites.
 *
 * Note: Full inlining of the Writer class is blocked by TypeScript type compatibility issues
 * with the @fern-api/python-ast types (AstNode, Reference, etc.) that reference the original Writer.
 * The actual implementation inlining will happen in a future PR once more AST types are ejected.
 */

export { Writer } from "@fern-api/python-ast/core/Writer";
