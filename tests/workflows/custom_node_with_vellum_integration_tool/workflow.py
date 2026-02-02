from vellum.workflows import BaseWorkflow

from .nodes.custom_node_with_integration_tool import CustomNodeWithIntegrationTool


class CustomNodeWithVellumIntegrationToolWorkflow(BaseWorkflow):
    graph = CustomNodeWithIntegrationTool
