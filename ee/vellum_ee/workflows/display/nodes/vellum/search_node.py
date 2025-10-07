from dataclasses import dataclass
from uuid import UUID
from typing import Dict, Generic, List, Optional, Tuple, Type, TypeVar, Union

from vellum import (
    MetadataFilterConfigRequest,
    VellumValueLogicalConditionGroupRequest,
    VellumValueLogicalConditionRequest,
)
from vellum.workflows.nodes.displayable.bases.types import MetadataLogicalCondition, MetadataLogicalConditionGroup
from vellum.workflows.nodes.displayable.search_node import SearchNode
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.vellum import InputVariablePointer
from vellum_ee.workflows.display.vellum import NodeInput

_SearchNodeType = TypeVar("_SearchNodeType", bound=SearchNode)


@dataclass
class VariableIdMap:
    id: Optional[UUID]
    lhs: Optional["VariableIdMap"]
    rhs: Optional["VariableIdMap"]


class BaseSearchNodeDisplay(BaseNodeDisplay[_SearchNodeType], Generic[_SearchNodeType]):
    # A mapping between the id of the operand (e.g. "lhs_variable_id" or "rhs_variable_id") and the id of the node input
    # that the operand is pointing to.
    metadata_filter_input_id_by_operand_id: Dict[UUID, UUID] = {}
    __serializable_inputs__ = {
        SearchNode.query,
        SearchNode.document_index,
        SearchNode.weights,
        SearchNode.chunk_separator,
        SearchNode.limit,
        SearchNode.result_merging,
    }

    def serialize(
        self, display_context: WorkflowDisplayContext, error_output_id: Optional[UUID] = None, **_kwargs
    ) -> JsonObject:
        node = self._node
        node_id = self.node_id
        node_inputs = self._generate_search_node_inputs(node_id, node, display_context)

        results_output_display = self.get_node_output_display(node.Outputs.results)
        text_output_display = self.get_node_output_display(node.Outputs.text)

        return {
            "id": str(node_id),
            "type": "SEARCH",
            "inputs": [node_input.dict() for node_input in node_inputs.values()],
            "data": {
                "label": self.label,
                "results_output_id": str(results_output_display.id),
                "text_output_id": str(text_output_display.id),
                "error_output_id": str(error_output_id) if error_output_id else None,
                "source_handle_id": str(self.get_source_handle_id(display_context.port_displays)),
                "target_handle_id": str(self.get_target_handle_id()),
                "query_node_input_id": str(node_inputs["query"].id),
                "document_index_node_input_id": str(node_inputs["document_index_id"].id),
                "weights_node_input_id": str(node_inputs["weights"].id),
                "limit_node_input_id": str(node_inputs["limit"].id),
                "separator_node_input_id": str(node_inputs["separator"].id),
                "result_merging_enabled_node_input_id": str(node_inputs["result_merging_enabled"].id),
                "external_id_filters_node_input_id": str(node_inputs["external_id_filters"].id),
                "metadata_filters_node_input_id": str(node_inputs["metadata_filters"].id),
            },
            **self.serialize_generic_fields(display_context, exclude=["outputs"]),
        }

    def _generate_search_node_inputs(
        self,
        node_id: UUID,
        node: Type[SearchNode],
        display_context: WorkflowDisplayContext,
    ) -> Dict[str, NodeInput]:
        node_inputs: Dict[str, NodeInput] = {}

        options = raise_if_descriptor(node.options)
        raw_filters = raise_if_descriptor(node.filters)
        filters = raw_filters if raw_filters else options.filters if options else None

        external_id_filters = filters.external_ids if filters else None

        raw_metadata_filters = filters.metadata if filters else None
        metadata_filters = None
        metadata_filters_node_inputs: list[NodeInput] = []
        if raw_metadata_filters:
            if isinstance(raw_metadata_filters, MetadataFilterConfigRequest):
                raise ValueError(
                    "MetadataFilterConfigRequest is deprecated. Please use VellumValueLogicalExpressionRequest instead."
                )
            metadata_filters, metadata_filters_node_inputs = self._serialize_logical_expression(
                raw_metadata_filters, display_context=display_context
            )

        raw_result_merging = raise_if_descriptor(node.result_merging)
        result_merging = raw_result_merging if raw_result_merging else options.result_merging if options else None
        result_merging_enabled = True if result_merging and result_merging.enabled else False

        raw_weights = raise_if_descriptor(node.weights)
        weights = raw_weights if raw_weights is not None else options.weights if options is not None else None

        raw_limit = raise_if_descriptor(node.limit)
        limit = raw_limit if raw_limit is not None else options.limit if options is not None else None

        node_input_names_and_values = [
            ("query", raise_if_descriptor(node.query)),
            ("document_index_id", raise_if_descriptor(node.document_index)),
            ("weights", weights.dict() if weights else None),
            ("limit", limit),
            ("separator", raise_if_descriptor(node.chunk_separator)),
            (
                "result_merging_enabled",
                ("True" if result_merging_enabled else "False"),
            ),
            ("external_id_filters", external_id_filters),
            ("metadata_filters", metadata_filters),
        ]

        for node_input_name, node_input_value in node_input_names_and_values:
            node_input = create_node_input(
                node_id,
                node_input_name,
                node_input_value,
                display_context,
                input_id=self.node_input_ids_by_name.get(node_input_name),
            )
            node_inputs[node_input_name] = node_input

        for node_input in metadata_filters_node_inputs:
            node_inputs[node_input.key] = node_input

        return node_inputs

    def _serialize_logical_expression(
        self,
        logical_expression: Union[
            VellumValueLogicalConditionGroupRequest,
            VellumValueLogicalConditionRequest,
            MetadataLogicalConditionGroup,
            MetadataLogicalCondition,
        ],
        display_context: WorkflowDisplayContext,
        path: List[int] = [],
    ) -> Tuple[JsonObject, List[NodeInput]]:
        if isinstance(logical_expression, VellumValueLogicalConditionGroupRequest):
            conditions: JsonArray = []
            variables = []
            for idx, condition in enumerate(logical_expression.conditions):
                serialized_condition, serialized_variables = self._serialize_logical_expression(
                    condition, display_context=display_context, path=path + [idx]
                )
                conditions.append(serialized_condition)
                variables.extend(serialized_variables)

            return (
                {
                    "type": "LOGICAL_CONDITION_GROUP",
                    "combinator": logical_expression.combinator,
                    "conditions": conditions,
                    "negated": logical_expression.negated,
                },
                variables,
            )
        elif isinstance(logical_expression, VellumValueLogicalConditionRequest):
            lhs_variable_id = logical_expression.lhs_variable.value
            if not isinstance(lhs_variable_id, str):
                raise TypeError(f"Expected lhs_variable_id to be a string, got {type(lhs_variable_id)}")

            rhs_variable_id = logical_expression.rhs_variable.value
            if not isinstance(rhs_variable_id, str):
                raise TypeError(f"Expected rhs_variable_id to be a string, got {type(rhs_variable_id)}")

            lhs_query_input_id: UUID = self.metadata_filter_input_id_by_operand_id.get(
                UUID(lhs_variable_id)
            ) or uuid4_from_hash(f"{self.node_id}|lhs|{hash(tuple(path))}")
            rhs_query_input_id: UUID = self.metadata_filter_input_id_by_operand_id.get(
                UUID(rhs_variable_id)
            ) or uuid4_from_hash(f"{self.node_id}|rhs|{hash(tuple(path))}")

            return (
                {
                    "type": "LOGICAL_CONDITION",
                    "lhs_variable_id": str(lhs_variable_id),
                    "operator": logical_expression.operator,
                    "rhs_variable_id": str(rhs_variable_id),
                },
                [
                    create_node_input(
                        self.node_id,
                        f"vellum-query-builder-variable-{lhs_variable_id}",
                        str(lhs_query_input_id),
                        display_context,
                        input_id=UUID(lhs_variable_id),
                        pointer_type=InputVariablePointer,
                    ),
                    create_node_input(
                        self.node_id,
                        f"vellum-query-builder-variable-{rhs_variable_id}",
                        str(rhs_query_input_id),
                        display_context,
                        input_id=UUID(rhs_variable_id),
                        pointer_type=InputVariablePointer,
                    ),
                ],
            )

        elif isinstance(logical_expression, MetadataLogicalConditionGroup):
            conditions = []
            variables = []
            for idx, metadata_condition in enumerate(logical_expression.conditions):
                serialized_condition, serialized_variables = self._serialize_logical_expression(
                    metadata_condition, display_context=display_context, path=path + [idx]
                )
                conditions.append(serialized_condition)
                variables.extend(serialized_variables)

            return (
                {
                    "type": "LOGICAL_CONDITION_GROUP",
                    "combinator": logical_expression.combinator,
                    "conditions": conditions,
                    "negated": logical_expression.negated,
                },
                variables,
            )

        elif isinstance(logical_expression, MetadataLogicalCondition):
            lhs_variable = logical_expression.lhs_variable
            rhs_variable = logical_expression.rhs_variable

            lhs_query_input_id = uuid4_from_hash(f"{self.node_id}|lhs|{hash(tuple(path))}")
            rhs_query_input_id = uuid4_from_hash(f"{self.node_id}|rhs|{hash(tuple(path))}")

            return (
                {
                    "type": "LOGICAL_CONDITION",
                    "lhs_variable_id": str(lhs_query_input_id),
                    "operator": logical_expression.operator,
                    "rhs_variable_id": str(rhs_query_input_id),
                },
                [
                    create_node_input(
                        self.node_id,
                        f"vellum-query-builder-variable-{lhs_query_input_id}",
                        lhs_variable,
                        display_context,
                        input_id=lhs_query_input_id,
                    ),
                    create_node_input(
                        self.node_id,
                        f"vellum-query-builder-variable-{rhs_query_input_id}",
                        rhs_variable,
                        display_context,
                        input_id=rhs_query_input_id,
                    ),
                ],
            )
        else:
            raise ValueError(f"Unsupported logical expression type: {type(logical_expression)}")
