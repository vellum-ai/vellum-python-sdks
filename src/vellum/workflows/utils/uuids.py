import hashlib
from uuid import UUID
from typing import TYPE_CHECKING

from vellum.workflows.utils.module_path import normalize_module_path

if TYPE_CHECKING:
    from vellum.workflows.inputs.base import BaseInputs
    from vellum.workflows.state.base import BaseState
    from vellum.workflows.triggers.base import BaseTrigger


def generate_workflow_deployment_prefix(deployment_name: str, release_tag: str) -> str:
    """
    Generate a workflow deployment prefix from deployment name and release tag.

    Args:
        deployment_name: The name of the workflow deployment
        release_tag: The release tag to resolve

    Returns:
        The generated prefix in format vellum_workflow_deployment_{hash}
    """
    expected_hash = str(uuid4_from_hash(f"{deployment_name}|{release_tag}")).replace("-", "_")
    return f"vellum_workflow_deployment_{expected_hash}"


def generate_entity_id_from_path(path: str) -> UUID:
    """
    Generate a deterministic entity ID from a path string.

    This function normalizes the path by filtering out any leading UUID namespace segment
    (which may change on each invocation when workflows are loaded dynamically), then
    generates a stable UUID from the normalized path.

    Args:
        path: The path string to generate an ID from (e.g., "a1b2c3d4-e5f6-7890-abcd-ef1234567890.workflow.MyNode")

    Returns:
        A deterministic UUID based on the normalized path
    """
    normalized_path = normalize_module_path(path)
    return uuid4_from_hash(normalized_path)


def uuid4_from_hash(input_str: str) -> UUID:
    # Create a SHA-256 hash of the input string
    hash_bytes = hashlib.sha256(input_str.encode()).digest()

    # Modify the hash to follow UUID4 structure
    # UUID4 has 8-4-4-4-12 hexadecimal characters
    # Version bits (4 bits) should be set to 4 (for UUID4),
    # and variant bits (2 bits) should start with 0b10

    # Convert first 16 bytes into UUID
    hash_list = list(hash_bytes[:16])

    # Set the version to 4 (UUID4)
    hash_list[6] = (hash_list[6] & 0x0F) | 0x40

    # Set the variant to 0b10xxxxxx
    hash_list[8] = (hash_list[8] & 0x3F) | 0x80

    # Create a UUID from the modified bytes
    return UUID(bytes=bytes(hash_list))


def get_trigger_attribute_id(trigger_class: "type[BaseTrigger]", attribute_name: str) -> UUID:
    """
    Generate a deterministic trigger attribute ID from a trigger class and attribute name
    using the class's module name, __qualname__, and attribute name to ensure stability and uniqueness.

    Args:
        trigger_class: The trigger class containing the attribute
        attribute_name: The name of the attribute

    Returns:
        A deterministic UUID based on the trigger class module, qualname, and attribute name
    """
    trigger_id = trigger_class.__id__
    return uuid4_from_hash(f"{trigger_id}|{attribute_name}")


def get_workflow_input_id(inputs_class: "type[BaseInputs]", input_name: str) -> UUID:
    """
    Generate a deterministic workflow input ID from an inputs class and input name
    using the class's parent workflow ID and input name to ensure stability and uniqueness.

    Args:
        inputs_class: The inputs class containing the input
        input_name: The name of the input

    Returns:
        A deterministic UUID based on the workflow ID and input name
    """
    workflow_class = inputs_class.__parent_class__
    workflow_id = workflow_class.__id__
    return uuid4_from_hash(f"{workflow_id}|inputs|id|{input_name}")


def get_state_value_id(state_class: "type[BaseState]", state_value_name: str) -> UUID:
    """
    Generate a deterministic state value ID from a state class and state value name
    using the class's module name, qualname, and state value name to ensure stability and uniqueness.

    Args:
        state_class: The state class containing the state value
        state_value_name: The name of the state value

    Returns:
        A deterministic UUID based on the state class module, qualname, and state value name
    """
    return uuid4_from_hash(f"{state_class.__module__}.{state_class.__qualname__}|state_values|id|{state_value_name}")
