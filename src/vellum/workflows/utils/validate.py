from typing import Any, Union, get_args, get_origin


class TypeValidationError(ValueError):
    """Exception raised when type validation fails."""

    def __init__(self, declared_type: type, target_type: type) -> None:
        declared_type_name = getattr(declared_type, "__name__", str(declared_type))
        target_type_name = getattr(target_type, "__name__", str(target_type))
        super().__init__(
            f"Output type mismatch: declared type '{declared_type_name}' "
            f"but the 'value' Output has type(s) '{target_type_name}'. "
        )
        self.declared_type = declared_type
        self.target_type = target_type


def validate_target_type(declared_type: type, target_type: type) -> None:
    # If either type is Any, validation always passes
    if declared_type is Any or target_type is Any:
        return

    declared_origin = get_origin(declared_type)
    target_origin = get_origin(target_type)

    # Special case: both are Unions
    # Each target union member must be compatible with at least one declared union member
    if declared_origin is Union and target_origin is Union:
        declared_union_args = get_args(declared_type)
        target_union_args = get_args(target_type)
        for target_member in target_union_args:
            is_compatible = False
            for declared_member in declared_union_args:
                try:
                    validate_target_type(declared_member, target_member)
                    is_compatible = True
                    break
                except TypeValidationError:
                    continue
            if not is_compatible:
                # This target member is not compatible with any declared member
                raise TypeValidationError(declared_type, target_type)
        # All target members are compatible with at least one declared member
        return

    # If declared_type is a Union, target_type must be compatible with at least one union member
    if declared_origin is Union:
        declared_union_args = get_args(declared_type)
        for union_member in declared_union_args:
            try:
                validate_target_type(union_member, target_type)
                # If any union member is compatible, validation passes
                return
            except TypeValidationError:
                # This union member is incompatible, try the next one
                continue
        # None of the union members are compatible with target_type
        raise TypeValidationError(declared_type, target_type)

    # If target_type is a Union, ALL union members must be compatible with declared_type
    if target_origin is Union:
        target_union_args = get_args(target_type)
        for union_member in target_union_args:
            try:
                validate_target_type(declared_type, union_member)
            except TypeValidationError:
                # At least one union member is incompatible with declared_type
                raise TypeValidationError(declared_type, target_type)
        # All union members are compatible with declared_type
        return

    # Check for exact type match
    if target_type == declared_type:
        return

    # Check for subclass relationships
    try:
        if issubclass(target_type, declared_type) or issubclass(declared_type, target_type):
            return
    except TypeError:
        # Handle cases where types aren't classes (e.g., generic types)
        if str(target_type) == str(declared_type):
            return

    # Check for generic type compatibility
    declared_origin = get_origin(declared_type)

    if target_origin is None and declared_origin is None:
        # Neither is a generic type, and they don't match
        raise TypeValidationError(declared_type, target_type)

    if target_origin == declared_type or declared_origin == target_type or target_origin == declared_origin:
        target_args = get_args(target_type)
        declared_args = get_args(declared_type)

        if len(declared_args) == 0:
            return

        if len(target_args) != len(declared_args):
            raise TypeValidationError(declared_type, target_type)

        for target_arg, declared_arg in zip(target_args, declared_args):
            validate_target_type(declared_arg, target_arg)

        return

    # If we reach here, types don't match
    raise TypeValidationError(declared_type, target_type)
