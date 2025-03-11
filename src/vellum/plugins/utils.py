import pydantic

IS_PYDANTIC_V1 = pydantic.VERSION.startswith("1.")
_loaded = False


def load_runtime_plugins() -> None:
    if IS_PYDANTIC_V1:
        # Pydantic plugins are only available in v2, so we defer the imports
        # below until we confirm we are running a supported version of pydantic
        return

    from pydantic.plugin import _loader as _pydantic_plugin_loader

    from vellum.plugins.pydantic import pydantic_plugin

    global _loaded
    if _loaded:
        return
    _loaded = True

    # TODO: This is a hack to get the Vellum plugin to load. We're supposed to use
    # pyproject.toml, but I couldn't figure out after an hour
    # https://app.shortcut.com/vellum/story/4635
    _pydantic_plugin_loader.get_plugins()
    if _pydantic_plugin_loader._plugins is not None:
        _pydantic_plugin_loader._plugins["vellum_plugin"] = pydantic_plugin
