class NodeValidationError(Exception):
    """Exception raised when a node fails validation during workflow display serialization."""

    def __init__(self, message: str, node_class_name: str):
        self.message = message
        self.node_class_name = node_class_name
        super().__init__(f"Node validation error in {node_class_name}: {message}")
