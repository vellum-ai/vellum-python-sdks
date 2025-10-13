export type CodegenErrorCode =
  | "PROJECT_SERIALIZATION_ERROR"
  | "WORKFLOW_GENERATION_ERROR"
  | "WORKFLOW_INPUT_GENERATION_ERROR"
  | "WORKFLOW_OUTPUT_GENERATION_ERROR"
  | "NODE_DEFINITION_GENERATION_ERROR"
  | "NODE_ATTRIBUTE_GENERATION_ERROR"
  | "NODE_PORT_GENERATION_ERROR"
  | "NODE_PORT_NOT_FOUND_ERROR"
  | "NODE_NOT_FOUND_ERROR"
  | "NODE_OUTPUT_NOT_FOUND_ERROR"
  | "NODE_INPUT_NOT_FOUND_ERROR"
  | "UNSUPPORTED_SANDBOX_INPUT_ERROR"
  | "ENTITY_NOT_FOUND_ERROR"
  | "POST_PROCESSING_ERROR"
  | "VALUE_GENERATION_ERROR"
  | "FILE_FORMATTING_ERROR";

export type CodegenErrorSeverity = "ERROR" | "WARNING";

export abstract class BaseCodegenError extends Error {
  abstract code: CodegenErrorCode;

  public readonly severity: CodegenErrorSeverity;

  constructor(message: string, severity?: CodegenErrorSeverity);
  constructor(
    message: string,
    options?: ErrorOptions & { severity?: CodegenErrorSeverity }
  );
  constructor(
    message: string,
    optionsOrSeverity?:
      | CodegenErrorSeverity
      | (ErrorOptions & { severity?: CodegenErrorSeverity })
  ) {
    const options =
      typeof optionsOrSeverity === "string" ? undefined : optionsOrSeverity;
    const severity =
      typeof optionsOrSeverity === "string"
        ? optionsOrSeverity
        : optionsOrSeverity?.severity;

    super(message, options);

    this.severity = severity ?? "ERROR";
    this.name = this.constructor.name;
  }

  public log() {
    if (this.severity === "ERROR") {
      console.error(this.message);
    } else {
      console.warn(this.message);
    }
  }
}

/**
 * An error that raises when deserializing the request to codegen
 * into a valid Workflow project.
 */
export class ProjectSerializationError extends BaseCodegenError {
  code = "PROJECT_SERIALIZATION_ERROR" as const;
}

/**
 * An error that raises when the Workflow definition fails to
 * generate.
 */
export class WorkflowGenerationError extends BaseCodegenError {
  code = "WORKFLOW_GENERATION_ERROR" as const;
}

/**
 * An error that raises when the Workflow Inpus fail to
 * generate.
 */
export class WorkflowInputGenerationError extends BaseCodegenError {
  code = "WORKFLOW_INPUT_GENERATION_ERROR" as const;
}

/**
 * An error that raises when the Workflow Outputs fail to
 * generate.
 */
export class WorkflowOutputGenerationError extends BaseCodegenError {
  code = "WORKFLOW_OUTPUT_GENERATION_ERROR" as const;
}

/**
 * An error that raises when the Node definition fails to generate
 */
export class NodeDefinitionGenerationError extends BaseCodegenError {
  code = "NODE_DEFINITION_GENERATION_ERROR" as const;
}

/**
 * An error that raises when generating a node attribute fails.
 */
export class NodeAttributeGenerationError extends BaseCodegenError {
  code = "NODE_ATTRIBUTE_GENERATION_ERROR" as const;
}

/**
 * An error that raises when generating a node port fails.
 */
export class NodePortGenerationError extends BaseCodegenError {
  code = "NODE_PORT_GENERATION_ERROR" as const;
}

/**
 * An error that raises when unable to find a node port.
 */
export class NodePortNotFoundError extends BaseCodegenError {
  code = "NODE_PORT_NOT_FOUND_ERROR" as const;
}

/**
 * An error that raises when a node is not found.
 */
export class NodeNotFoundError extends BaseCodegenError {
  code = "NODE_NOT_FOUND_ERROR" as const;
}

/**
 * An error that raises when a vellum entity is not found.
 */
export class EntityNotFoundError extends BaseCodegenError {
  code = "ENTITY_NOT_FOUND_ERROR" as const;
}

/**
 * An error that raises when a sandbox input is not supported.
 */
export class UnsupportedSandboxInputError extends BaseCodegenError {
  code = "UNSUPPORTED_SANDBOX_INPUT_ERROR" as const;
}

/**
 * An error that raises when a node output is not found.
 */
export class NodeOutputNotFoundError extends BaseCodegenError {
  code = "NODE_OUTPUT_NOT_FOUND_ERROR" as const;
}

/**
 * An error that raises when a node input is not found.
 */
export class NodeInputNotFoundError extends BaseCodegenError {
  code = "NODE_INPUT_NOT_FOUND_ERROR" as const;
}

/**
 * An error that raises when a value fails to generate
 */
export class ValueGenerationError extends BaseCodegenError {
  code = "VALUE_GENERATION_ERROR" as const;
}
/**
 * An error that raises when file formatting fails.
 */
export class FileFormattingError extends BaseCodegenError {
  code = "FILE_FORMATTING_ERROR" as const;
}
