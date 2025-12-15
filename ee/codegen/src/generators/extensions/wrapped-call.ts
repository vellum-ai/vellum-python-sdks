import { AstNode } from "./ast-node";
import { MethodInvocation } from "./method-invocation";
import { Writer } from "./writer";

/**
 * Represents a wrapped function call pattern: wrapper(...)(inner)
 * This is used for patterns like tool(...)(func)
 */
export declare namespace WrappedCall {
  interface Args {
    /** The wrapper function invocation (e.g., tool(...)) */
    wrapper: MethodInvocation;
    /** The inner value to pass to the wrapper result (e.g., the function reference) */
    inner: AstNode;
  }
}

export class WrappedCall extends AstNode {
  private readonly wrapper: MethodInvocation;
  private readonly inner: AstNode;

  constructor({ wrapper, inner }: WrappedCall.Args) {
    super();
    this.wrapper = wrapper;
    this.inner = inner;
    this.inheritReferences(wrapper);
    this.inheritReferences(inner);
  }

  write(writer: Writer): void {
    // Write wrapper(...)(inner)
    this.wrapper.write(writer);
    writer.write("(");
    this.inner.write(writer);
    writer.write(")");
  }
}
