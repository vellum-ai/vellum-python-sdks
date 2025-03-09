from typing import Any, Iterator, Tuple, Type, Union, get_args, get_origin
from typing_extensions import dataclass_transform

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import WorkflowInitializationException
from vellum.workflows.references import ExternalInputReference, WorkflowInputReference
from vellum.workflows.references.input import InputReference
from vellum.workflows.types.utils import get_class_attr_names, infer_types


@dataclass_transform(kw_only_default=True)
class _BaseInputsMeta(type):
    def __getattribute__(cls, name: str) -> Any:
        if not name.startswith("_") and name in cls.__annotations__ and issubclass(cls, BaseInputs):
            instance = vars(cls).get(name)
            types = infer_types(cls, name)

            if getattr(cls, "__descriptor_class__", None) is ExternalInputReference:
                return ExternalInputReference(name=name, types=types, instance=instance, inputs_class=cls)
            else:
                return WorkflowInputReference(name=name, types=types, instance=instance, inputs_class=cls)

        return super().__getattribute__(name)

    def __iter__(cls) -> Iterator[InputReference]:
        # We iterate through the inheritance hierarchy to find all the WorkflowInputReference attached to this
        # Inputs class. __mro__ is the method resolution order, which is the order in which base classes are resolved.
        for resolved_cls in cls.__mro__:
            attr_names = get_class_attr_names(resolved_cls)
            for attr_name in attr_names:
                attr_value = getattr(resolved_cls, attr_name)
                if not isinstance(attr_value, (WorkflowInputReference, ExternalInputReference)):
                    continue

                yield attr_value


class BaseInputs(metaclass=_BaseInputsMeta):
    __parent_class__: Type = type(None)

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize BaseInputs with provided keyword arguments.

        Validation logic:
        1. Ensures all required fields (non-Optional types) either:
        - Have a value provided in kwargs, or
        - Have a default value defined in the class
        2. Validates that no None values are provided for required fields
        3. Sets all provided values as attributes on the instance

        Args:
            **kwargs: Keyword arguments corresponding to the class's type annotations

        Raises:
            WorkflowInitializationException: If a required field is missing or None
        """
        for name, field_type in self.__class__.__annotations__.items():
            # Get the value (either from kwargs or class default)
            value = kwargs.get(name)
            has_default = name in vars(self.__class__)

            if value is None and not has_default:
                # Check if field_type allows None
                origin = get_origin(field_type)
                args = get_args(field_type)
                if not (origin is Union and type(None) in args):
                    raise WorkflowInitializationException(
                        message=f"Required input variables {name} should have defined value",
                        code=WorkflowErrorCode.INVALID_INPUTS,
                    )

            # If value provided in kwargs, set it on the instance
            if name in kwargs:
                setattr(self, name, value)

    def __iter__(self) -> Iterator[Tuple[InputReference, Any]]:
        for input_descriptor in self.__class__:
            if hasattr(self, input_descriptor.name):
                yield (input_descriptor, getattr(self, input_descriptor.name))

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.is_instance_schema(cls)
