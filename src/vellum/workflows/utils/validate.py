from typing import Union, get_args, get_origin


def validate_target_type(declared_type: type, target_type: type) -> None:
    # If target_type is a Union, check if declared_type matches any of the union members
    target_origin = get_origin(target_type)
    if target_origin is Union:
        target_union_args = get_args(target_type)
        for union_member in target_union_args:
            try:
                validate_target_type(declared_type, union_member)
                return  # If any union member matches, validation succeeds
            except ValueError:
                continue
        # If none of the union members matched, raise an error
        declared_type_name = getattr(declared_type, "__name__", str(declared_type))
        target_type_name = getattr(target_type, "__name__", str(target_type))
        raise ValueError(
            f"Output type mismatch: declared type '{declared_type_name}' "
            f"but the 'value' Output has type(s) {target_type_name}. "
        )

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
        declared_type_name = getattr(declared_type, "__name__", str(declared_type))
        target_type_name = getattr(target_type, "__name__", str(target_type))
        raise ValueError(
            f"Output type mismatch: declared type '{declared_type_name}' "
            f"but the 'value' Output has type(s) {target_type_name}. "
        )

    if target_origin == declared_type or declared_origin == target_type or target_origin == declared_origin:
        target_args = get_args(target_type)
        declared_args = get_args(declared_type)

        if len(declared_args) == 0:
            return

        if len(target_args) != len(declared_args):
            declared_type_name = getattr(declared_type, "__name__", str(declared_type))
            target_type_name = getattr(target_type, "__name__", str(target_type))
            raise ValueError(
                f"Output type mismatch: declared type '{declared_type_name}' "
                f"but the 'value' Output has type(s) {target_type_name}. "
            )

        for target_arg, declared_arg in zip(target_args, declared_args):
            validate_target_type(declared_arg, target_arg)

        return

    # If we reach here, types don't match
    declared_type_name = getattr(declared_type, "__name__", str(declared_type))
    target_type_name = getattr(target_type, "__name__", str(target_type))
    raise ValueError(
        f"Output type mismatch: declared type '{declared_type_name}' "
        f"but the 'value' Output has type(s) {target_type_name}. "
    )
