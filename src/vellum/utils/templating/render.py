import ast
import json
from typing import Any, Callable, Dict, Optional, Union

from jinja2.sandbox import SandboxedEnvironment

from vellum.utils.templating.exceptions import JinjaTemplateError
from vellum.workflows.state.encoder import DefaultStateEncoder


def finalize(obj: Any) -> str:
    if isinstance(obj, (dict, list)):
        return json.dumps(obj, cls=DefaultStateEncoder)

    if isinstance(obj, str):
        try:
            data = ast.literal_eval(obj)
            if isinstance(data, (dict, list)):
                return json.dumps(data, cls=DefaultStateEncoder)
        except (ValueError, SyntaxError):
            pass

    return str(obj)


def render_sandboxed_jinja_template(
    *,
    template: str,
    input_values: Dict[str, Any],
    jinja_custom_filters: Optional[Dict[str, Callable[[Union[str, bytes]], bool]]] = None,
    jinja_globals: Optional[Dict[str, Any]] = None,
) -> str:
    """Render a Jinja template within a sandboxed environment."""
    prepared_input_values = {}
    for key, value in input_values.items():
        if isinstance(value, list):
            prepared_input_values[key] = json.loads(json.dumps(value, cls=DefaultStateEncoder))
        else:
            prepared_input_values[key] = value

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

        jinja_template = environment.from_string(template)

        if jinja_globals:
            jinja_template.globals.update(jinja_globals)

        rendered_template = jinja_template.render(prepared_input_values)
    except json.JSONDecodeError as e:
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
