from vellum._lazy import make_lazy_loader

_LAZY_IMPORTS = {
    # constants
    "APIRequestMethod": (".constants", "APIRequestMethod"),
    "AuthorizationType": (".constants", "AuthorizationType"),
    # errors
    "WorkflowErrorCode": (".errors.types", "WorkflowErrorCode"),
    # exceptions
    "NodeException": (".exceptions", "NodeException"),
    # inputs
    "BaseInputs": (".inputs", "BaseInputs"),
    "DatasetRow": (".inputs", "DatasetRow"),
    # nodes - base
    "BaseNode": (".nodes", "BaseNode"),
    # nodes - core
    "ErrorNode": (".nodes", "ErrorNode"),
    "InlineSubworkflowNode": (".nodes", "InlineSubworkflowNode"),
    "MapNode": (".nodes", "MapNode"),
    "RetryNode": (".nodes", "RetryNode"),
    "TemplatingNode": (".nodes", "TemplatingNode"),
    "TryNode": (".nodes", "TryNode"),
    # nodes - displayable
    "APINode": (".nodes", "APINode"),
    "BaseInlinePromptNode": (".nodes", "BaseInlinePromptNode"),
    "BasePromptDeploymentNode": (".nodes", "BasePromptDeploymentNode"),
    "BaseSearchNode": (".nodes", "BaseSearchNode"),
    "CodeExecutionNode": (".nodes", "CodeExecutionNode"),
    "ConditionalNode": (".nodes", "ConditionalNode"),
    "FinalOutputNode": (".nodes", "FinalOutputNode"),
    "GuardrailNode": (".nodes", "GuardrailNode"),
    "InlinePromptNode": (".nodes", "InlinePromptNode"),
    "NoteNode": (".nodes", "NoteNode"),
    "PromptDeploymentNode": (".nodes", "PromptDeploymentNode"),
    "SearchNode": (".nodes", "SearchNode"),
    "SubworkflowDeploymentNode": (".nodes", "SubworkflowDeploymentNode"),
    "WebSearchNode": (".nodes", "WebSearchNode"),
    # nodes - special
    "ToolCallingNode": (".nodes.displayable.tool_calling_node", "ToolCallingNode"),
    "MockNodeExecution": (".nodes.mocks", "MockNodeExecution"),
    # ports
    "Port": (".ports", "Port"),
    # references
    "EnvironmentVariableReference": (".references.environment_variable", "EnvironmentVariableReference"),
    "LazyReference": (".references.lazy", "LazyReference"),
    # runner
    "WorkflowRunner": (".runner", "WorkflowRunner"),
    # sandbox
    "WorkflowSandboxRunner": (".sandbox", "WorkflowSandboxRunner"),
    # state
    "BaseState": (".state.base", "BaseState"),
    # triggers
    "IntegrationTrigger": (".triggers", "IntegrationTrigger"),
    "ScheduleTrigger": (".triggers", "ScheduleTrigger"),
    # types
    "Json": (".types.core", "Json"),
    "MergeBehavior": (".types.core", "MergeBehavior"),
    "DeploymentDefinition": (".types.definition", "DeploymentDefinition"),
    "MCPServer": (".types.definition", "MCPServer"),
    "VellumIntegrationToolDefinition": (".types.definition", "VellumIntegrationToolDefinition"),
    # workflows
    "BaseWorkflow": (".workflows", "BaseWorkflow"),
}

__getattr__, __dir__ = make_lazy_loader(__name__, _LAZY_IMPORTS)

__all__ = [
    "APINode",
    "APIRequestMethod",
    "AuthorizationType",
    "BaseInlinePromptNode",
    "BaseInputs",
    "BaseNode",
    "BasePromptDeploymentNode",
    "BaseSearchNode",
    "BaseState",
    "BaseWorkflow",
    "CodeExecutionNode",
    "ConditionalNode",
    "DatasetRow",
    "DeploymentDefinition",
    "EnvironmentVariableReference",
    "ErrorNode",
    "FinalOutputNode",
    "GuardrailNode",
    "InlinePromptNode",
    "InlineSubworkflowNode",
    "IntegrationTrigger",
    "Json",
    "LazyReference",
    "MapNode",
    "MCPServer",
    "MergeBehavior",
    "MockNodeExecution",
    "NodeException",
    "NoteNode",
    "Port",
    "PromptDeploymentNode",
    "RetryNode",
    "ScheduleTrigger",
    "SearchNode",
    "SubworkflowDeploymentNode",
    "TemplatingNode",
    "ToolCallingNode",
    "TryNode",
    "VellumIntegrationToolDefinition",
    "WebSearchNode",
    "WorkflowErrorCode",
    "WorkflowRunner",
    "WorkflowSandboxRunner",
]
