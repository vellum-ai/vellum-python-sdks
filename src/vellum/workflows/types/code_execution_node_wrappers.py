from vellum.client.types.function_call import FunctionCall


class StringValueWrapper(str):
    def __getitem__(self, key):
        if key == "value":
            return self
        if key == "type":
            return "STRING"
        return super().__getitem__(key)

    def __getattr__(self, attr):
        if attr == "value":
            return self
        if attr == "type":
            return "STRING"
        raise AttributeError(f"'str' object has no attribute '{attr}'")


class FunctionCallWrapper(FunctionCall):
    def __init__(self, obj):
        super().__init__(arguments=obj.arguments, name=obj.name, id=obj.id)

    def __getitem__(self, key):
        if key == "value":
            return self
        if key == "type":
            return "FUNCTION_CALL"
        raise KeyError(key)

    def __getattr__(self, attr):
        if attr == "value":
            return self
        if attr == "type":
            return "FUNCTION_CALL"
        raise AttributeError(f"'FunctionCall' object has no attribute '{attr}'")


class ListWrapper(list):
    def __getitem__(self, key):
        item = super().__getitem__(key)
        if not isinstance(item, DictWrapper) and not isinstance(item, ListWrapper):
            self.__setitem__(key, clean_for_dict_wrapper(item))

        return super().__getitem__(key)

    def __getattr__(self, attr):
        if attr == "value":
            return self
        raise AttributeError(f"'list' object has no attribute '{attr}'")

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]


class DictWrapper(dict):
    """
    This wraps a dict object to make it behave basically the same as a standard javascript object
    and enables us to use vellum types here without a shared library since we don't actually
    typecheck things here.
    """

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __getattr__(self, attr):
        if attr not in self:
            if attr == "value":
                # In order to be backwards compatible with legacy Workflows, which wrapped
                # several values as VellumValue objects, we use the "value" key to return itself
                return self

            raise AttributeError(f"dict has no key: '{attr}'")

        item = super().__getitem__(attr)
        if not isinstance(item, DictWrapper) and not isinstance(item, ListWrapper):
            self.__setattr__(attr, clean_for_dict_wrapper(item))

        return super().__getitem__(attr)

    def __setattr__(self, name, value):
        self[name] = value


def clean_for_dict_wrapper(obj):
    if isinstance(obj, dict):
        wrapped = DictWrapper(obj)
        for key in wrapped.keys():
            wrapped[key] = clean_for_dict_wrapper(wrapped[key])

        return wrapped

    elif isinstance(obj, list):
        return ListWrapper(map(lambda item: clean_for_dict_wrapper(item), obj))
    elif isinstance(obj, str):
        return StringValueWrapper(obj)
    elif isinstance(obj, FunctionCall):
        return FunctionCallWrapper(obj)

    return obj
