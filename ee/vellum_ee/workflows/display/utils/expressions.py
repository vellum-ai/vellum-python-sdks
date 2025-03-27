from typing import TYPE_CHECKING

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.references.lazy import LazyReference

if TYPE_CHECKING:
    from vellum_ee.workflows.display.types import WorkflowDisplayContext


def get_child_descriptor(value: LazyReference, display_context: "WorkflowDisplayContext") -> BaseDescriptor:
    if isinstance(value._get, str):
        reference_parts = value._get.split(".")
        if len(reference_parts) < 3:
            raise Exception(f"Failed to parse lazy reference: {value._get}. Only Node Output references are supported.")

        output_name = reference_parts[-1]
        nested_class_name = reference_parts[-2]
        if nested_class_name != "Outputs":
            raise Exception(
                f"Failed to parse lazy reference: {value._get}. Outputs are the only node reference supported."
            )

        node_class_name = ".".join(reference_parts[:-2])
        for node in display_context.node_displays.keys():
            if node.__name__ == node_class_name:
                return getattr(node.Outputs, output_name)

        raise Exception(f"Failed to parse lazy reference: {value._get}")

    return value._get()
