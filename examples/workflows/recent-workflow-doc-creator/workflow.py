from vellum.workflows import BaseWorkflow

from .nodes.comments_output import CommentsOutput
from .nodes.deployments_output import DeploymentsOutput
from .nodes.fetch_recent_deployments import FetchRecentDeployments
from .nodes.pr_urls_output import PrUrlsOutput
from .nodes.process_deployments import ProcessDeployments
from .triggers.scheduled import Scheduled


class Workflow(BaseWorkflow):
    graph = (
        Scheduled
        >> FetchRecentDeployments
        >> ProcessDeployments
        >> {
            DeploymentsOutput,
            CommentsOutput,
            PrUrlsOutput,
        }
    )

    class Outputs(BaseWorkflow.Outputs):
        pr_results = PrUrlsOutput.Outputs.value
        deployments_processed = CommentsOutput.Outputs.value
        deployments_json = DeploymentsOutput.Outputs.value
