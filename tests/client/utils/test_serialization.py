# This file was auto-generated by Fern from our API Definition.

from typing import List, Any

from vellum.client.core.serialization import convert_and_respect_annotation_metadata
from .assets.models import ShapeParams, ObjectWithOptionalFieldParams


UNION_TEST: ShapeParams = {"radius_measurement": 1.0, "shape_type": "circle", "id": "1"}
UNION_TEST_CONVERTED = {"shapeType": "circle", "radiusMeasurement": 1.0, "id": "1"}


def test_convert_and_respect_annotation_metadata() -> None:
    data: ObjectWithOptionalFieldParams = {
        "string": "string",
        "long_": 12345,
        "bool_": True,
        "literal": "lit_one",
        "any": "any",
    }
    converted = convert_and_respect_annotation_metadata(
        object_=data, annotation=ObjectWithOptionalFieldParams, direction="write"
    )
    assert converted == {"string": "string", "long": 12345, "bool": True, "literal": "lit_one", "any": "any"}


def test_convert_and_respect_annotation_metadata_in_list() -> None:
    data: List[ObjectWithOptionalFieldParams] = [
        {"string": "string", "long_": 12345, "bool_": True, "literal": "lit_one", "any": "any"},
        {"string": "another string", "long_": 67890, "list_": [], "literal": "lit_one", "any": "any"},
    ]
    converted = convert_and_respect_annotation_metadata(
        object_=data, annotation=List[ObjectWithOptionalFieldParams], direction="write"
    )

    assert converted == [
        {"string": "string", "long": 12345, "bool": True, "literal": "lit_one", "any": "any"},
        {"string": "another string", "long": 67890, "list": [], "literal": "lit_one", "any": "any"},
    ]


def test_convert_and_respect_annotation_metadata_in_nested_object() -> None:
    data: ObjectWithOptionalFieldParams = {
        "string": "string",
        "long_": 12345,
        "union": UNION_TEST,
        "literal": "lit_one",
        "any": "any",
    }
    converted = convert_and_respect_annotation_metadata(
        object_=data, annotation=ObjectWithOptionalFieldParams, direction="write"
    )

    assert converted == {
        "string": "string",
        "long": 12345,
        "union": UNION_TEST_CONVERTED,
        "literal": "lit_one",
        "any": "any",
    }


def test_convert_and_respect_annotation_metadata_in_union() -> None:
    converted = convert_and_respect_annotation_metadata(object_=UNION_TEST, annotation=ShapeParams, direction="write")

    assert converted == UNION_TEST_CONVERTED


def test_convert_and_respect_annotation_metadata_with_empty_object() -> None:
    data: Any = {}
    converted = convert_and_respect_annotation_metadata(object_=data, annotation=ShapeParams, direction="write")
    assert converted == data
