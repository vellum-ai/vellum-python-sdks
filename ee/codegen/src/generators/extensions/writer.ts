import fs from "node:fs/promises";

import { Writer as FernWriter } from "@fern-api/python-ast/core/Writer";
import { Config } from "@wasm-fmt/ruff_fmt";

const wasm = new URL(
  "../../../node_modules/@wasm-fmt/ruff_fmt/ruff_fmt_bg.wasm",
  import.meta.url
);

const module_or_path = fs.readFile(wasm);

export class Writer extends FernWriter {
  async toStringFormatted(config?: Config) {
    // This method copies the original method from the FernWriter class, but
    // it passes a proper input to the `init` function from ruff to silence the
    // deprecation warning from Ruff.
    const { default: init, format } = await import("@wasm-fmt/ruff_fmt");
    await init({ module_or_path });
    return format(this.buffer, undefined, config);
  }
}
