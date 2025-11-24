from typing import get_origin


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

        descriptor_origin = get_origin(target_type)
        declared_origin = get_origin(declared_type)

        if descriptor_origin is None and declared_origin is None:
            continue

        if descriptor_origin == declared_type or declared_origin == target_type or descriptor_origin == declared_origin:
            type_mismatch = False
            break

    if type_mismatch:
        declared_type_name = getattr(declared_type, "__name__", str(declared_type))
        descriptor_type_names = [getattr(t, "__name__", str(t)) for t in target_types]

        raise ValueError(
            f"Output type mismatch: declared type '{declared_type_name}' "
            f"but the 'value' Output has type(s) {descriptor_type_names}. "
        )
