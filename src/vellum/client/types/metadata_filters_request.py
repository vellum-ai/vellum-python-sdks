# This file was auto-generated by Fern from our API Definition.

import typing
from .metadata_filter_config_request import MetadataFilterConfigRequest
from .vellum_value_logical_expression_request import VellumValueLogicalExpressionRequest

MetadataFiltersRequest = typing.Union[MetadataFilterConfigRequest, VellumValueLogicalExpressionRequest]
