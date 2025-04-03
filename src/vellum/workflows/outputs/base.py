from typing import TYPE_CHECKING, Any, Generic, Iterator, Set, Tuple, Type, TypeVar, Union, cast
from typing_extensions import dataclass_transform

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

from vellum.workflows.constants import undefined
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.references.output import OutputReference
from vellum.workflows.types.utils import get_class_attr_names, infer_types

if TYPE_CHECKING:
    from vellum.workflows.nodes.bases.base import BaseNode

_Delta = TypeVar("_Delta")
_Accumulated = TypeVar("_Accumulated")


class BaseOutput(Generic[_Delta, _Accumulated]):
    _value: Union[_Accumulated, Type[undefined]]
    _delta: Union[_Delta, Type[undefined]]
    _name: str

    def __init__(
        self,
        name: str,
        value: Union[_Accumulated, Type[undefined]] = undefined,
        delta: Union[_Delta, Type[undefined]] = undefined,
    ) -> None:
        if value is not undefined and delta is not undefined:
            raise ValueError("Cannot set both value and delta")

        self._name = name.replace("-", "_")  # Convert hyphens to underscores for valid python variable names
        self._value = value
        self._delta = delta

    @property
    def delta(self) -> Union[_Delta, Type[undefined]]:
        return self._delta

    @property
    def value(self) -> Union[_Accumulated, Type[undefined]]:
        return self._value

    @property
    def is_initiated(self) -> bool:
        return self._delta is undefined and self._value is undefined

    @property
    def is_streaming(self) -> bool:
        return self._delta is not undefined and self._value is undefined

    @property
    def is_fulfilled(self) -> bool:
        return self._delta is undefined and self._value is not undefined

    @property
    def name(self) -> str:
        return self._name

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.is_instance_schema(cls)

    def serialize(self) -> dict:
        data: dict[str, Any] = {
            "name": self.name,
        }

        if self.value is not undefined:
            data["value"] = self.value

        if self.delta is not undefined:
            data["delta"] = self.delta

        return data

    def __repr__(self) -> str:
        if self.value is not undefined:
            return f"{self.__class__.__name__}({self.name}={self.value})"
        elif self.delta is not undefined:
            return f"{self.__class__.__name__}({self.name}={self.delta})"
        else:
            return f"{self.__class__.__name__}(name='{self.name}')"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, BaseOutput):
            return False

        return self.name == other.name and self.value == other.value and self.delta == other.delta

    def __hash__(self) -> int:
        return hash((self._name, self._value, self._value))


@dataclass_transform(kw_only_default=True)
class _BaseOutputsMeta(type):
    def __eq__(cls, other: Any) -> bool:
        """
        We need to include custom eq logic to prevent infinite loops during ipython reloading.
        """

        if not isinstance(other, _BaseOutputsMeta):
            return False

        if not cls.__qualname__.endswith(".Outputs") or not other.__qualname__.endswith(".Outputs"):
            return super().__eq__(other)

        self_outputs_class = cast(Type["BaseNode.Outputs"], cls)
        other_outputs_class = cast(Type["BaseNode.Outputs"], other)

        if not hasattr(self_outputs_class, "_node_class") or not hasattr(other_outputs_class, "_node_class"):
            return super().__eq__(other)

        if self_outputs_class._node_class is None or other_outputs_class._node_class is None:
            return super().__eq__(other)

        return getattr(self_outputs_class._node_class, "__qualname__") == getattr(
            other_outputs_class._node_class, "__qualname__"
        )

    def __setattr__(cls, name: str, value: Any) -> None:
        if isinstance(value, OutputReference):
            # During module reload, tools like ipython will set class attributes from the get attribute
            # from the old class. Our getattribute dynamically returns OutputDescriptors, which means during
            # module reload, it will override the class' original default value with its own OutputReference.
            # We want to avoid this, so we check if the name of the class and the name of the descriptor
            # are the same, and if they are, we don't set the attribute.
            if f"{cls.__qualname__}.{name}" == str(value):
                return super().__setattr__(name, value.instance)

        return super().__setattr__(name, value)

    def __getattribute__(cls, name: str) -> Any:
        if name.startswith("_") or not issubclass(cls, BaseOutputs):
            return super().__getattribute__(name)

        attr_names = get_class_attr_names(cls)
        if name in attr_names:
            # We first try to resolve the instance that this class attribute name is mapped to. If it's not found,
            # we iterate through its inheritance hierarchy to find the first base class that has this attribute
            # and use its mapping.
            instance = vars(cls).get(name, undefined)
            if instance is undefined:
                for base in cls.__mro__[1:]:
                    if hasattr(base, name):
                        instance = getattr(base, name)
                        break

            types = infer_types(cls, name)
            return OutputReference(
                name=name,
                types=types,
                instance=instance,
                outputs_class=cls,
            )

        return super().__getattribute__(name)

    def __hash__(self) -> int:
        return hash(self.__qualname__)

    def __iter__(cls) -> Iterator[OutputReference]:
        # We iterate through the inheritance hierarchy to find all the OutputDescriptors attached to this Outputs class.
        # __mro__ is the method resolution order, which is the order in which base classes are resolved.
        yielded_attr_names: Set[str] = set()

        for resolved_cls in cls.__mro__:
            attr_names = get_class_attr_names(resolved_cls)
            for attr_name in attr_names:
                if attr_name in yielded_attr_names:
                    continue

                attr_value = getattr(resolved_cls, attr_name)
                if not isinstance(attr_value, OutputReference):
                    continue

                yield attr_value
                yielded_attr_names.add(attr_name)


class BaseOutputs(metaclass=_BaseOutputsMeta):
    def __init__(self, **kwargs: Any) -> None:
        declared_fields = {descriptor.name for descriptor in self.__class__}
        provided_fields = set(kwargs.keys())

        if not provided_fields.issubset(declared_fields):
            raise NodeException(
                message=f"Unexpected outputs: {provided_fields - declared_fields}",
                code=WorkflowErrorCode.INVALID_OUTPUTS,
            )

        for name, value in kwargs.items():
            setattr(self, name, value)

        if hasattr(self, "_outputs_post_init") and callable(self._outputs_post_init):
            self._outputs_post_init(**kwargs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (dict, BaseOutputs)):
            return super().__eq__(other)

        outputs = {ref.name: value for ref, value in self if value is not undefined}
        return outputs == other

    def __repr__(self) -> str:
        values = f"{', '.join(f'{ref.name}={value}' for ref, value in self if value is not undefined)}"
        return f"{self.__class__.__name__}({values})"

    def __iter__(self) -> Iterator[Tuple[OutputReference, Any]]:
        for output_descriptor in self.__class__:
            output_value = getattr(self, output_descriptor.name, undefined)
            if isinstance(output_value, BaseDescriptor):
                output_value = undefined

            yield (output_descriptor, output_value)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.is_instance_schema(cls)
