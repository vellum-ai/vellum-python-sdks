import typing

from pydantic import ValidationInfo, field_validator

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.client.types.ml_model_hosting_interface import MlModelHostingInterface


def _extract_literal_values(union_type: typing.Any) -> set[str]:
    """Extract literal values from a Union[Literal[...], typing.Any] type."""
    valid_values: set[str] = set()
    args = typing.get_args(union_type)
    for arg in args:
        if typing.get_origin(arg) is typing.Literal:
            valid_values.update(typing.get_args(arg))
    return valid_values


# Extract valid literal values from MlModelHostingInterface (excluding typing.Any fallback)
VALID_HOSTING_INTERFACES = _extract_literal_values(MlModelHostingInterface)


class MLModel(UniversalBaseModel):
    """
    Represents an ML model with its name and hosting interface.
    """

    name: str
    hosted_by: MlModelHostingInterface

    @field_validator("hosted_by", mode="before")
    @classmethod
    def validate_hosted_by(cls, value: str, info: ValidationInfo) -> str:
        """Validate that hosted_by is one of the valid literal values."""
        if value not in VALID_HOSTING_INTERFACES:
            raise ValueError(f"Invalid hosting interface: {value}. Must be one of {sorted(VALID_HOSTING_INTERFACES)}")
        return value
