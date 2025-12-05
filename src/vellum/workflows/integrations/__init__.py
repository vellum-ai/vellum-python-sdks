from vellum._lazy import make_lazy_loader

_LAZY_IMPORTS = {
    "ComposioService": (".composio_service", "ComposioService"),
    "MCPService": (".mcp_service", "MCPService"),
    "VellumIntegrationService": (".vellum_integration_service", "VellumIntegrationService"),
}

__getattr__, __dir__ = make_lazy_loader(__name__, _LAZY_IMPORTS)

__all__ = ["ComposioService", "MCPService", "VellumIntegrationService"]
