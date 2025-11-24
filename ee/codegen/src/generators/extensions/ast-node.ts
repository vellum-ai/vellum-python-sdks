/**
 * Re-export AstNode from @fern-api/python-ast/core/AstNode
 * This centralizes the import path as part of the effort to eject from the python-ast package.
 *
 * All consumers should import AstNode from this module instead of directly from @fern-api/python-ast.
 * This allows us to eventually replace the implementation without updating all import sites.
 *
 * Note: Full inlining of the AstNode class is blocked by TypeScript type compatibility issues
 * with the @fern-api/python-ast types that reference the original AstNode.
 * The actual implementation inlining will happen in a future PR once more AST types are ejected.
 */

export { AstNode } from "@fern-api/python-ast/core/AstNode";
