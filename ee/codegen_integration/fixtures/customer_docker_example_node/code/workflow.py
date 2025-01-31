from vellum.workflows import BaseWorkflow

from .nodes.db_query_node import DBQueryNode


class CustomDockerImageWorkflow(BaseWorkflow):
    graph = DBQueryNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = DBQueryNode.Outputs.rows
