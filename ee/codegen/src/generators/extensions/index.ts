/**
 * This directory contains custom AST Nodes and classes that should one day be contributed to Fern's python-ast package.
 * We do this to unblock critical functionality for our users to avoid forking the package or being blocked on the
 * upstream package being updated.
 *
 * The process usually entails:
 * 1. Creating a new file in this directory that supports the new functionality you need.
 * 2. Exporting the new class from this file to use in the rest of codegen.
 * 3. In parallel, create a PR at https://github.com/fern-api/fern/tree/main/generators/python-v2/ast
 * 4. Once the PR is merged, update the dependency from our dedicated branch: https://github.com/fern-api/fern/pull/5100
 * 5. Remove the custom code in this directory and use the new AST Node from the upstream package.
 */

export * from "./protected-python-file";
export * from "./custom-comment";
export * from "./custom-class";
export * from "./python-utils";
