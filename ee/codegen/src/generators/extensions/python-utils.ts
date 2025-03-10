import { Class } from "@fern-api/python-ast/Class";

import { CustomClass } from "./custom-class";
import { CustomComment } from "./custom-comment";

export namespace python {
  export function customComment(args: CustomComment.Args): CustomComment {
    return new CustomComment(args);
  }

  export function class_(args: Class.Args): Class {
    const customClass = new CustomClass({
      name: args.name,
      docs: args.docs,
      extends_: args.extends_,
      decorators: args.decorators,
    });

    return customClass as unknown as Class;
  }
}
