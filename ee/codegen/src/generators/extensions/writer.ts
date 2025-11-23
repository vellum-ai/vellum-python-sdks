/**
 * Re-export Writer from @fern-api/python-ast/core/Writer
 * This centralizes the import path as part of the effort to eject from the python-ast package.
 *
 * All consumers should import Writer from this module instead of directly from @fern-api/python-ast.
 * This allows us to eventually replace the implementation without updating all import sites.
 */

export { Writer } from "@fern-api/python-ast/core/Writer";
