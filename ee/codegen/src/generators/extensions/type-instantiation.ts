import { AstNode } from "src/generators/extensions/ast-node";

/**
 * Base class for all type instantiation AST nodes.
 * This is an empty class that serves as a marker for type instantiation nodes
 * so that they can be identified via instanceof checks.
 */
export abstract class TypeInstantiation extends AstNode {}
