from typing import Any, Iterator, Tuple, Type
from typing_extensions import dataclass_transform

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

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
        for name, value in kwargs.items():
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
