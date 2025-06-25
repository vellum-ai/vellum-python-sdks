import {
  OperatorMapping,
  WorkflowExpression as WorkflowExpressionType,
  WorkflowValueDescriptorReference as WorkflowValueDescriptorReferenceType,
  WorkflowValueDescriptor as WorkflowValueDescriptorType,
} from "src/types/vellum";

export function convertOperatorType(
  workflowValueDescriptor: WorkflowValueDescriptorType
): OperatorMapping {
  if (!isExpression(workflowValueDescriptor)) {
    return "equals"; // default operator if not an expression
  }

  const operator = workflowValueDescriptor.operator;
  if (!operator) {
    return "equals"; // default operator if operator is null
  }

  const operatorMappings: Record<string, OperatorMapping> = {
    "=": "equals",
    "!=": "does_not_equal",
    "<": "less_than",
    ">": "greater_than",
    "<=": "less_than_or_equal_to",
    ">=": "greater_than_or_equal_to",
    contains: "contains",
    beginsWith: "begins_with",
    endsWith: "ends_with",
    doesNotContain: "does_not_contain",
    doesNotBeginWith: "does_not_begin_with",
    doesNotEndWith: "does_not_end_with",
    null: "is_null",
    notNull: "is_not_null",
    in: "in",
    notIn: "not_in",
    between: "between",
    notBetween: "not_between",
    blank: "is_blank",
    notBlank: "is_not_blank",
    parseJson: "parse_json",
    coalesce: "coalesce",
    accessField: "access_field",
    or: "or",
    and: "and",
    isError: "is_error",
  };

  return operatorMappings[operator] || "equals"; // return default operator if not found
}

export function isExpression(
  workflowValueDescriptor: WorkflowValueDescriptorType
): workflowValueDescriptor is WorkflowExpressionType {
  return (
    workflowValueDescriptor.type === "UNARY_EXPRESSION" ||
    workflowValueDescriptor.type === "BINARY_EXPRESSION" ||
    workflowValueDescriptor.type === "TERNARY_EXPRESSION"
  );
}

export function isReference(
  workflowValueDescriptor: WorkflowValueDescriptorType
): workflowValueDescriptor is WorkflowValueDescriptorReferenceType {
  return (
    workflowValueDescriptor.type === "NODE_OUTPUT" ||
    workflowValueDescriptor.type === "WORKFLOW_INPUT" ||
    workflowValueDescriptor.type === "WORKFLOW_STATE" ||
    workflowValueDescriptor.type === "CONSTANT_VALUE" ||
    workflowValueDescriptor.type === "VELLUM_SECRET" ||
    workflowValueDescriptor.type === "ENVIRONMENT_VARIABLE" ||
    workflowValueDescriptor.type === "EXECUTION_COUNTER" ||
    workflowValueDescriptor.type === "DICTIONARY_REFERENCE" ||
    workflowValueDescriptor.type === "ARRAY_REFERENCE"
  );
}
