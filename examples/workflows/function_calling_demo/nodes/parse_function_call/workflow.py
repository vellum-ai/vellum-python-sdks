from vellum.workflows import BaseWorkflow

from .nodes.allowed_function_names import AllowedFunctionNames
from .nodes.args import Args
from .nodes.conditional_node import ConditionalNode1
from .nodes.conditional_node_1 import ConditionalNode2
from .nodes.error_message import ErrorMessage
from .nodes.error_node import ErrorNode1
from .nodes.error_node_1 import ErrorNode2
from .nodes.is_valid_function_name import IsValidFunctionName
from .nodes.merge_node import MergeNode
from .nodes.name import Name
from .nodes.parse_function_args import ParseFunctionArgs
from .nodes.parse_function_call import ParseFunctionCall1
from .nodes.parse_function_name import ParseFunctionName
from .nodes.parse_tool_id import ParseToolID
from .nodes.tool_id import ToolID


class ParseFunctionCallWorkflow(BaseWorkflow):
    graph = ParseFunctionCall1 >> {
        ConditionalNode1.Ports.branch_1 >> ErrorNode2,
        ConditionalNode1.Ports.branch_2
        >> {
            ParseFunctionName,
            ParseFunctionArgs,
            AllowedFunctionNames,
            ParseToolID,
        }
        >> MergeNode
        >> IsValidFunctionName
        >> {
            ConditionalNode2.Ports.branch_1
            >> {
                Name,
                Args,
                ToolID,
            },
            ConditionalNode2.Ports.branch_2 >> ErrorMessage >> ErrorNode1,
        },
    }

    class Outputs(BaseWorkflow.Outputs):
        function_args = Args.Outputs.value
        function_name = Name.Outputs.value
        tool_id = ToolID.Outputs.value
