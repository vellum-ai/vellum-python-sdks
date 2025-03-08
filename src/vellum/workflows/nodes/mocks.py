from functools import reduce
from uuid import UUID
from typing import TYPE_CHECKING, Any, List, Literal, Optional, Sequence, Type, Union

from pydantic import ConfigDict, ValidationError

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.client.types.array_vellum_value import ArrayVellumValue
from vellum.client.types.vellum_value import VellumValue
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import WorkflowInitializationException
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.references.constant import ConstantValueReference

if TYPE_CHECKING:
    from vellum.workflows import BaseWorkflow

import logging

logger = logging.getLogger(__name__)


class _RawLogicalCondition(UniversalBaseModel):
    type: Literal["LOGICAL_CONDITION"] = "LOGICAL_CONDITION"
    lhs_variable_id: UUID
    operator: Literal["==", ">", ">=", "<", "<=", "!="]
    rhs_variable_id: UUID


class _RawLogicalConditionGroup(UniversalBaseModel):
    type: Literal["LOGICAL_CONDITION_GROUP"] = "LOGICAL_CONDITION_GROUP"
    conditions: List["_RawLogicalExpression"]
    combinator: Literal["AND", "OR"]
    negated: bool


_RawLogicalExpression = Union[_RawLogicalCondition, _RawLogicalConditionGroup]


class _RawLogicalExpressionVariable(UniversalBaseModel):
    id: UUID


class _RawMockWorkflowNodeExecutionConstantValuePointer(_RawLogicalExpressionVariable):
    type: Literal["CONSTANT_VALUE"] = "CONSTANT_VALUE"
    variable_value: VellumValue


class _RawMockWorkflowNodeExecutionNodeExecutionCounterPointer(_RawLogicalExpressionVariable):
    type: Literal["EXECUTION_COUNTER"] = "EXECUTION_COUNTER"
    node_id: UUID


class _RawMockWorkflowNodeExecutionInputVariablePointer(_RawLogicalExpressionVariable):
    type: Literal["INPUT_VARIABLE"] = "INPUT_VARIABLE"
    input_variable_id: UUID


class _RawMockWorkflowNodeExecutionNodeOutputPointer(_RawLogicalExpressionVariable):
    type: Literal["NODE_OUTPUT"] = "NODE_OUTPUT"
    node_id: UUID
    input_id: UUID


class _RawMockWorkflowNodeExecutionNodeInputPointer(_RawLogicalExpressionVariable):
    type: Literal["NODE_INPUT"] = "NODE_INPUT"
    node_id: UUID
    input_id: UUID


_RawMockWorkflowNodeExecutionValuePointer = Union[
    _RawMockWorkflowNodeExecutionConstantValuePointer,
    _RawMockWorkflowNodeExecutionNodeExecutionCounterPointer,
    _RawMockWorkflowNodeExecutionInputVariablePointer,
    _RawMockWorkflowNodeExecutionNodeOutputPointer,
    _RawMockWorkflowNodeExecutionNodeInputPointer,
]


class _RawMockWorkflowNodeWhenCondition(UniversalBaseModel):
    expression: _RawLogicalExpression
    variables: List[_RawMockWorkflowNodeExecutionValuePointer]


class _RawMockWorkflowNodeThenOutput(UniversalBaseModel):
    output_id: UUID
    value: _RawMockWorkflowNodeExecutionValuePointer


class _RawMockWorkflowNodeExecution(UniversalBaseModel):
    when_condition: _RawMockWorkflowNodeWhenCondition
    then_outputs: List[_RawMockWorkflowNodeThenOutput]


class _RawMockWorkflowNodeConfig(UniversalBaseModel):
    type: Literal["WORKFLOW_NODE_OUTPUT"] = "WORKFLOW_NODE_OUTPUT"
    node_id: UUID
    mock_executions: List[_RawMockWorkflowNodeExecution]


class MockNodeExecution(UniversalBaseModel):
    when_condition: BaseDescriptor
    then_outputs: BaseOutputs

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @staticmethod
    def validate_all(
        raw_mock_workflow_node_configs: Optional[List[Any]],
        workflow: Type["BaseWorkflow"],
    ) -> Optional[List["MockNodeExecution"]]:
        if not raw_mock_workflow_node_configs:
            return None

        ArrayVellumValue.model_rebuild()
        try:
            mock_workflow_node_configs = [
                _RawMockWorkflowNodeConfig.model_validate(raw_mock_workflow_node_config)
                for raw_mock_workflow_node_config in raw_mock_workflow_node_configs
            ]
        except ValidationError as e:
            raise WorkflowInitializationException(
                message="Failed to validate mock node executions",
                code=WorkflowErrorCode.INVALID_INPUTS,
            ) from e

        nodes = {node.__id__: node for node in workflow.get_nodes()}
        node_output_name_by_id = {
            node.__output_ids__[output.name]: output.name for node in workflow.get_nodes() for output in node.Outputs
        }

        # We need to support the old way that the Vellum App's WorkflowRunner used to define Node Mocks in order to
        # avoid needing to update the mock resolution strategy that it and the frontend uses. The path towards
        # cleaning this up will go as follows:
        # 1. Release Mock support in SDK-Enabled Workflows
        # 2. Deprecate Mock support in non-SDK enabled Workflows, encouraging users to migrate to SDK-enabled Workflows
        # 3. Remove the old mock resolution strategy
        # 4. Update this SDK to handle the new mock resolution strategy with WorkflowValueDescriptors
        # 5. Cutover the Vellum App to the new mock resolution strategy
        # 6. Remove the old mock resolution strategy from this SDK
        def _translate_raw_logical_expression(
            raw_logical_expression: _RawLogicalExpression,
            raw_variables: List[_RawMockWorkflowNodeExecutionValuePointer],
        ) -> BaseDescriptor:
            if raw_logical_expression.type == "LOGICAL_CONDITION":
                return _translate_raw_logical_condition(raw_logical_expression, raw_variables)
            else:
                return _translate_raw_logical_condition_group(raw_logical_expression, raw_variables)

        def _translate_raw_logical_condition_group(
            raw_logical_condition_group: _RawLogicalConditionGroup,
            raw_variables: List[_RawMockWorkflowNodeExecutionValuePointer],
        ) -> BaseDescriptor:
            if not raw_logical_condition_group.conditions:
                return ConstantValueReference(True)

            conditions = [
                _translate_raw_logical_expression(condition, raw_variables)
                for condition in raw_logical_condition_group.conditions
            ]
            return reduce(
                lambda acc, condition: (
                    acc and condition if raw_logical_condition_group.combinator == "AND" else acc or condition
                ),
                conditions,
            )

        def _translate_raw_logical_condition(
            raw_logical_condition: _RawLogicalCondition,
            raw_variables: List[_RawMockWorkflowNodeExecutionValuePointer],
        ) -> BaseDescriptor:
            variable_by_id = {v.id: v for v in raw_variables}
            lhs = _translate_raw_logical_expression_variable(variable_by_id[raw_logical_condition.lhs_variable_id])
            rhs = _translate_raw_logical_expression_variable(variable_by_id[raw_logical_condition.rhs_variable_id])
            if raw_logical_condition.operator == ">":
                return lhs.greater_than(rhs)
            elif raw_logical_condition.operator == ">=":
                return lhs.greater_than_or_equal_to(rhs)
            elif raw_logical_condition.operator == "<":
                return lhs.less_than(rhs)
            elif raw_logical_condition.operator == "<=":
                return lhs.less_than_or_equal_to(rhs)
            elif raw_logical_condition.operator == "==":
                return lhs.equals(rhs)
            elif raw_logical_condition.operator == "!=":
                return lhs.does_not_equal(rhs)
            else:
                raise WorkflowInitializationException(f"Unsupported logical operator: {raw_logical_condition.operator}")

        def _translate_raw_logical_expression_variable(
            raw_variable: _RawMockWorkflowNodeExecutionValuePointer,
        ) -> BaseDescriptor:
            if raw_variable.type == "CONSTANT_VALUE":
                return ConstantValueReference(raw_variable.variable_value.value)
            elif raw_variable.type == "EXECUTION_COUNTER":
                node = nodes[raw_variable.node_id]
                return node.Execution.count
            else:
                raise WorkflowInitializationException(f"Unsupported logical expression type: {raw_variable.type}")

        mock_node_executions = []
        for mock_workflow_node_config in mock_workflow_node_configs:
            for mock_execution in mock_workflow_node_config.mock_executions:
                try:
                    when_condition = _translate_raw_logical_expression(
                        mock_execution.when_condition.expression,
                        mock_execution.when_condition.variables,
                    )

                    then_outputs = nodes[mock_workflow_node_config.node_id].Outputs()
                    for then_output in mock_execution.then_outputs:
                        node_output_name = node_output_name_by_id.get(then_output.output_id)
                        if node_output_name is None:
                            raise WorkflowInitializationException(
                                f"Output {then_output.output_id} not found in node {mock_workflow_node_config.node_id}"
                            )

                        resolved_output_reference = _translate_raw_logical_expression_variable(then_output.value)
                        if isinstance(resolved_output_reference, ConstantValueReference):
                            setattr(
                                then_outputs,
                                node_output_name,
                                resolved_output_reference._value,
                            )
                        else:
                            raise WorkflowInitializationException(
                                f"Unsupported resolved output reference type: {type(resolved_output_reference)}"
                            )

                    mock_node_executions.append(
                        MockNodeExecution(
                            when_condition=when_condition,
                            then_outputs=then_outputs,
                        )
                    )
                except Exception as e:
                    logger.exception("Failed to validate mock node execution", exc_info=e)
                    continue

        return mock_node_executions


MockNodeExecutionArg = Sequence[Union[BaseOutputs, MockNodeExecution]]
