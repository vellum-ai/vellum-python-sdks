from typing import get_args, get_origin


def validate_target_types(declared_type: type, target_types: tuple[type, ...]) -> None:
    type_mismatch = True
    for target_type in target_types:
        if target_type == declared_type:
            type_mismatch = False
            break

        try:
            if issubclass(target_type, declared_type) or issubclass(declared_type, target_type):
                type_mismatch = False
                break
        except TypeError:
            # Handle cases where types aren't classes (e.g., Union)
            if str(target_type) == str(declared_type):
                type_mismatch = False
                break

        target_origin = get_origin(target_type)
        declared_origin = get_origin(declared_type)

        if target_origin is None and declared_origin is None:
            continue

        if target_origin == declared_type or declared_origin == target_type or target_origin == declared_origin:
            target_args = get_args(target_type)
            declared_args = get_args(declared_type)
            if len(declared_args) == 0:
                type_mismatch = False
                break

            if len(target_args) != len(declared_args):
                continue

            type_args_match = True
            for target_arg, declared_arg in zip(target_args, declared_args):
                try:
                    validate_target_types(declared_arg, (target_arg,))
                except ValueError:
                    type_args_match = False
                    break

            type_mismatch = not type_args_match
            break

    if type_mismatch:
        declared_type_name = getattr(declared_type, "__name__", str(declared_type))
        descriptor_type_names = [getattr(t, "__name__", str(t)) for t in target_types]

        raise ValueError(
            f"Output type mismatch: declared type '{declared_type_name}' "
            f"but the 'value' Output has type(s) {descriptor_type_names}. "
        )
