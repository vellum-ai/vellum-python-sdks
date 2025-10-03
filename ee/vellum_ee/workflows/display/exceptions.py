class NodeValidationError(Exception):
    """Exception raised when a node fails validation during workflow display serialization."""

    def __init__(self, message: str, node_class_name: str):
        self.message = message
        self.node_class_name = node_class_name
        super().__init__(f"Node validation error in {node_class_name}: {message}")


class InvalidInputReferenceError(Exception):
    """Exception raised when a node references a non-existent workflow input."""

    def __init__(self, message: str, inputs_class_name: str, attribute_name: str):
        self.message = message
        self.inputs_class_name = inputs_class_name
        self.attribute_name = attribute_name
        super().__init__(f"Invalid input reference in {inputs_class_name}: {message}")
