class UserFacingException(Exception):
    def to_message(self) -> str:
        return str(self)


class UnsupportedSerializationException(UserFacingException):
    pass


class NodeValidationError(UserFacingException):
    """Exception raised when a node fails validation during workflow display serialization."""

    def __init__(self, message: str, node_class_name: str):
        self.message = message
        self.node_class_name = node_class_name
        super().__init__(f"Node validation error in {node_class_name}: {message}")


class InvalidInputReferenceError(UserFacingException):
    """Exception raised when a node references a non-existent workflow input."""

    def __init__(self, message: str, inputs_class_name: str, attribute_name: str):
        self.message = message
        self.inputs_class_name = inputs_class_name
        self.attribute_name = attribute_name
        super().__init__(f"Invalid input reference in {inputs_class_name}.{attribute_name}: {message}")


class InvalidOutputReferenceError(UserFacingException):
    """Exception raised when a node references a non-existent output."""

    pass


class WorkflowValidationError(UserFacingException):
    """Exception raised when a workflow fails validation during display serialization."""

    def __init__(self, message: str, workflow_class_name: str):
        self.message = message
        self.workflow_class_name = workflow_class_name
        super().__init__(f"Workflow validation error in {workflow_class_name}: {message}")


class TriggerValidationError(UserFacingException):
    """Exception raised when a trigger fails validation during serialization."""

    def __init__(self, message: str, trigger_class_name: str):
        self.message = message
        self.trigger_class_name = trigger_class_name
        super().__init__(f"Trigger validation error in {trigger_class_name}: {message}")


class StateValidationError(UserFacingException):
    """Exception raised when a state class fails validation during serialization."""

    def __init__(self, message: str, state_class_name: str, attribute_name: str):
        self.message = message
        self.state_class_name = state_class_name
        self.attribute_name = attribute_name
        super().__init__(f"State validation error in {state_class_name}.{attribute_name}: {message}")
