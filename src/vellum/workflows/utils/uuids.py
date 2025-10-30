import hashlib
from uuid import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
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
