from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.api_node import APINode
from .nodes.conditional_node import ConditionalNode
from .nodes.faa_document_store import FAADocumentStore
from .nodes.final_output_2 import FinalOutput2
from .nodes.formatted_search_results import FormattedSearchResults
from .nodes.most_recent_message import MostRecentMessage
from .nodes.prompt_node import PromptNode
from .nodes.prompt_node_14 import PromptNode14
from .nodes.prompt_node_16 import PromptNode16
from .nodes.prompt_node_18 import PromptNode18
from .nodes.prompt_node_19 import PromptNode19
from .nodes.prompt_node_9 import PromptNode9
from .nodes.subworkflow_node import SubworkflowNode
from .nodes.templating_node import TemplatingNode
from .nodes.templating_node_15 import TemplatingNode15


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = (
        MostRecentMessage
        >> PromptNode
        >> TemplatingNode
        >> {
            ConditionalNode.Ports.branch_1 >> SubworkflowNode >> PromptNode14,
            ConditionalNode.Ports.branch_4 >> PromptNode19,
            ConditionalNode.Ports.branch_3 >> FAADocumentStore >> FormattedSearchResults >> PromptNode9,
            ConditionalNode.Ports.branch_2 >> PromptNode16 >> TemplatingNode15 >> APINode >> PromptNode18,
        }
        >> FinalOutput2
    )

    class Outputs(BaseWorkflow.Outputs):
        answer = FinalOutput2.Outputs.value
