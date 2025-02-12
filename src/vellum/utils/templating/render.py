import json
from typing import Any, Callable, Dict, Optional, Union

from jinja2.sandbox import SandboxedEnvironment

from vellum.utils.templating.exceptions import JinjaTemplateError
from vellum.workflows.state.encoder import DefaultStateEncoder


def finalize(obj: Any) -> str:
    if isinstance(obj, dict):
        return json.dumps(obj, cls=DefaultStateEncoder)

    return str(obj)


def custom_replace(s, old, new):
    """
    Custom replace filter that uses DefaultStateEncoder for conversion
    """
    import json

    from vellum.workflows.state.encoder import DefaultStateEncoder

    def encode(obj):
        try:
            return json.dumps(obj, cls=DefaultStateEncoder)
        except TypeError:
            return str(obj)

    s_str = encode(s)
    old_str = encode(old)
    new_str = encode(new)

    return s_str.replace(old_str, new_str)


def render_sandboxed_jinja_template(
    *,
    template: str,
    input_values: Dict[str, Any],
    jinja_custom_filters: Optional[Dict[str, Callable[[Union[str, bytes]], bool]]] = None,
    jinja_globals: Optional[Dict[str, Any]] = None,
) -> str:
    """Render a Jinja template within a sandboxed environment."""

    try:
        environment = SandboxedEnvironment(
            keep_trailing_newline=True,
            finalize=finalize,
        )
        environment.policies["json.dumps_kwargs"] = {
            "cls": DefaultStateEncoder,
        }

        if jinja_custom_filters:
            environment.filters.update(jinja_custom_filters)

        environment.filters["replace"] = custom_replace

        jinja_template = environment.from_string(template)

        if jinja_globals:
            jinja_template.globals.update(jinja_globals)

        rendered_template = jinja_template.render(input_values)
    except json.JSONDecodeError as e:
        if not e.doc:
            raise JinjaTemplateError("Unable to render jinja template:\n" "Cannot run json.loads() on empty input")
        if e.msg == "Invalid control character at":
            raise JinjaTemplateError(
                "Unable to render jinja template:\n"
                "Cannot run json.loads() on JSON containing control characters. "
                "Use json.loads(input, strict=False) instead.",
            )

        raise JinjaTemplateError(
            f"Unable to render jinja template:\nCannot run json.loads() on invalid JSON\n{e.args[0]}"
        )
    except Exception as e:
        raise JinjaTemplateError(f"Unable to render jinja template:\n{e.args[0]}")

    return rendered_template
