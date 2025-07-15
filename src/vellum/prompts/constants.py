from vellum import PromptParameters

DEFAULT_PROMPT_PARAMETERS = PromptParameters(
    stop=[],
    temperature=0.0,
    max_tokens=4096,
    top_p=1.0,
    top_k=0,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    logit_bias=None,
    custom_parameters=None,
)
