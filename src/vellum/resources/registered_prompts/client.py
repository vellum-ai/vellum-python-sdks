# This file was auto-generated by Fern from our API Definition.

import typing
import urllib.parse
from json.decoder import JSONDecodeError

from ...core.api_error import ApiError
from ...core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ...core.jsonable_encoder import jsonable_encoder
from ...errors.bad_request_error import BadRequestError
from ...errors.conflict_error import ConflictError
from ...errors.not_found_error import NotFoundError
from ...types.provider_enum import ProviderEnum
from ...types.register_prompt_error_response import RegisterPromptErrorResponse
from ...types.register_prompt_model_parameters_request import RegisterPromptModelParametersRequest
from ...types.register_prompt_prompt_info_request import RegisterPromptPromptInfoRequest
from ...types.register_prompt_response import RegisterPromptResponse

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


class RegisteredPromptsClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def register_prompt(
        self,
        *,
        label: str,
        name: str,
        prompt: RegisterPromptPromptInfoRequest,
        provider: typing.Optional[ProviderEnum] = OMIT,
        model: str,
        parameters: RegisterPromptModelParametersRequest,
        meta: typing.Optional[typing.Dict[str, typing.Any]] = OMIT,
    ) -> RegisterPromptResponse:
        """
        Registers a prompt within Vellum and creates associated Vellum entities. Intended to be used by integration
        partners, not directly by Vellum users.

        Under the hood, this endpoint creates a new sandbox, a new model version, and a new deployment.

        Parameters:
            - label: str. A human-friendly label for corresponding entities created in Vellum.

            - name: str. A uniquely-identifying name for corresponding entities created in Vellum.

            - prompt: RegisterPromptPromptInfoRequest. Information about how to execute the prompt template.

            - provider: typing.Optional[ProviderEnum]. The initial LLM provider to use for this prompt

                                                       * `ANTHROPIC` - Anthropic
                                                       * `AWS_BEDROCK` - AWS Bedrock
                                                       * `AZURE_OPENAI` - Azure OpenAI
                                                       * `COHERE` - Cohere
                                                       * `GOOGLE` - Google
                                                       * `HOSTED` - Hosted
                                                       * `MOSAICML` - MosaicML
                                                       * `OPENAI` - OpenAI
                                                       * `FIREWORKS_AI` - Fireworks AI
                                                       * `HUGGINGFACE` - HuggingFace
                                                       * `MYSTIC` - Mystic
                                                       * `PYQ` - Pyq
                                                       * `REPLICATE` - Replicate
            - model: str. The initial model to use for this prompt

            - parameters: RegisterPromptModelParametersRequest. The initial model parameters to use for  this prompt

            - meta: typing.Optional[typing.Dict[str, typing.Any]]. Optionally include additional metadata to store along with the prompt.
        ---
        from vellum import (
            PromptTemplateBlockDataRequest,
            ProviderEnum,
            RegisterPromptModelParametersRequest,
            RegisterPromptPromptInfoRequest,
        )
        from vellum.client import Vellum

        client = Vellum(
            api_key="YOUR_API_KEY",
        )
        client.registered_prompts.register_prompt(
            label="string",
            name="string",
            prompt=RegisterPromptPromptInfoRequest(
                prompt_block_data=PromptTemplateBlockDataRequest(
                    version=1,
                    blocks=[],
                ),
                input_variables=[],
            ),
            provider=ProviderEnum.ANTHROPIC,
            model="string",
            parameters=RegisterPromptModelParametersRequest(
                temperature=1.1,
                max_tokens=1,
                top_p=1.1,
                frequency_penalty=1.1,
                presence_penalty=1.1,
            ),
        )
        """
        _request: typing.Dict[str, typing.Any] = {
            "label": label,
            "name": name,
            "prompt": prompt,
            "model": model,
            "parameters": parameters,
        }
        if provider is not OMIT:
            _request["provider"] = provider
        if meta is not OMIT:
            _request["meta"] = meta
        _response = self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_environment().default}/", "v1/registered-prompts/register"
            ),
            json=jsonable_encoder(_request),
            headers=self._client_wrapper.get_headers(),
            timeout=None,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(RegisterPromptResponse, _response.json())  # type: ignore
        if _response.status_code == 400:
            raise BadRequestError(pydantic.parse_obj_as(typing.Any, _response.json()))  # type: ignore
        if _response.status_code == 404:
            raise NotFoundError(pydantic.parse_obj_as(typing.Any, _response.json()))  # type: ignore
        if _response.status_code == 409:
            raise ConflictError(pydantic.parse_obj_as(RegisterPromptErrorResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncRegisteredPromptsClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def register_prompt(
        self,
        *,
        label: str,
        name: str,
        prompt: RegisterPromptPromptInfoRequest,
        provider: typing.Optional[ProviderEnum] = OMIT,
        model: str,
        parameters: RegisterPromptModelParametersRequest,
        meta: typing.Optional[typing.Dict[str, typing.Any]] = OMIT,
    ) -> RegisterPromptResponse:
        """
        Registers a prompt within Vellum and creates associated Vellum entities. Intended to be used by integration
        partners, not directly by Vellum users.

        Under the hood, this endpoint creates a new sandbox, a new model version, and a new deployment.

        Parameters:
            - label: str. A human-friendly label for corresponding entities created in Vellum.

            - name: str. A uniquely-identifying name for corresponding entities created in Vellum.

            - prompt: RegisterPromptPromptInfoRequest. Information about how to execute the prompt template.

            - provider: typing.Optional[ProviderEnum]. The initial LLM provider to use for this prompt

                                                       * `ANTHROPIC` - Anthropic
                                                       * `AWS_BEDROCK` - AWS Bedrock
                                                       * `AZURE_OPENAI` - Azure OpenAI
                                                       * `COHERE` - Cohere
                                                       * `GOOGLE` - Google
                                                       * `HOSTED` - Hosted
                                                       * `MOSAICML` - MosaicML
                                                       * `OPENAI` - OpenAI
                                                       * `FIREWORKS_AI` - Fireworks AI
                                                       * `HUGGINGFACE` - HuggingFace
                                                       * `MYSTIC` - Mystic
                                                       * `PYQ` - Pyq
                                                       * `REPLICATE` - Replicate
            - model: str. The initial model to use for this prompt

            - parameters: RegisterPromptModelParametersRequest. The initial model parameters to use for  this prompt

            - meta: typing.Optional[typing.Dict[str, typing.Any]]. Optionally include additional metadata to store along with the prompt.
        ---
        from vellum import (
            PromptTemplateBlockDataRequest,
            ProviderEnum,
            RegisterPromptModelParametersRequest,
            RegisterPromptPromptInfoRequest,
        )
        from vellum.client import AsyncVellum

        client = AsyncVellum(
            api_key="YOUR_API_KEY",
        )
        await client.registered_prompts.register_prompt(
            label="string",
            name="string",
            prompt=RegisterPromptPromptInfoRequest(
                prompt_block_data=PromptTemplateBlockDataRequest(
                    version=1,
                    blocks=[],
                ),
                input_variables=[],
            ),
            provider=ProviderEnum.ANTHROPIC,
            model="string",
            parameters=RegisterPromptModelParametersRequest(
                temperature=1.1,
                max_tokens=1,
                top_p=1.1,
                frequency_penalty=1.1,
                presence_penalty=1.1,
            ),
        )
        """
        _request: typing.Dict[str, typing.Any] = {
            "label": label,
            "name": name,
            "prompt": prompt,
            "model": model,
            "parameters": parameters,
        }
        if provider is not OMIT:
            _request["provider"] = provider
        if meta is not OMIT:
            _request["meta"] = meta
        _response = await self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_environment().default}/", "v1/registered-prompts/register"
            ),
            json=jsonable_encoder(_request),
            headers=self._client_wrapper.get_headers(),
            timeout=None,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(RegisterPromptResponse, _response.json())  # type: ignore
        if _response.status_code == 400:
            raise BadRequestError(pydantic.parse_obj_as(typing.Any, _response.json()))  # type: ignore
        if _response.status_code == 404:
            raise NotFoundError(pydantic.parse_obj_as(typing.Any, _response.json()))  # type: ignore
        if _response.status_code == 409:
            raise ConflictError(pydantic.parse_obj_as(RegisterPromptErrorResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
