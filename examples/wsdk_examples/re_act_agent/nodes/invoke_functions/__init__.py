from vellum.workflows.nodes.displayable import MapNode

from ..function_calls_to_json_array import FunctionCallsToJSONArray
from .workflow import InvokeFunctionsWorkflow


class InvokeFunctions(MapNode):
    items = FunctionCallsToJSONArray.Outputs.result
    subworkflow = InvokeFunctionsWorkflow
    max_concurrency = 4
