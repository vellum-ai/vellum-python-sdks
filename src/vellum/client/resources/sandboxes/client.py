# This file was auto-generated by Fern from our API Definition.

import typing
from ...core.client_wrapper import SyncClientWrapper
from ...core.request_options import RequestOptions
from ...types.deployment_read import DeploymentRead
from ...core.jsonable_encoder import jsonable_encoder
from ...core.pydantic_utilities import parse_obj_as
from json.decoder import JSONDecodeError
from ...core.api_error import ApiError
from ...types.named_scenario_input_request import NamedScenarioInputRequest
from ...types.sandbox_scenario import SandboxScenario
from ...core.serialization import convert_and_respect_annotation_metadata
from ...core.client_wrapper import AsyncClientWrapper

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


class SandboxesClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def deploy_prompt(
        self,
        id: str,
        prompt_variant_id: str,
        *,
        prompt_deployment_id: typing.Optional[str] = OMIT,
        prompt_deployment_name: typing.Optional[str] = OMIT,
        label: typing.Optional[str] = OMIT,
        release_tags: typing.Optional[typing.Sequence[str]] = OMIT,
        release_description: typing.Optional[str] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> DeploymentRead:
        """
        Parameters
        ----------
        id : str
            A UUID string identifying this sandbox.

        prompt_variant_id : str
            An ID identifying the Prompt you'd like to deploy.

        prompt_deployment_id : typing.Optional[str]
            The Vellum-generated ID of the Prompt Deployment you'd like to update. Cannot specify both this and prompt_deployment_name. Leave null to create a new Prompt Deployment.

        prompt_deployment_name : typing.Optional[str]
            The unique name of the Prompt Deployment you'd like to either create or update. Cannot specify both this and prompt_deployment_id. If provided and matches an existing Prompt Deployment, that Prompt Deployment will be updated. Otherwise, a new Prompt Deployment will be created.

        label : typing.Optional[str]
            In the event that a new Prompt Deployment is created, this will be the label it's given.

        release_tags : typing.Optional[typing.Sequence[str]]
            Optionally provide the release tags that you'd like to be associated with the latest release of the created/updated Prompt Deployment.

        release_description : typing.Optional[str]
            Optionally provide a description that details what's new in this Release.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        DeploymentRead


        Examples
        --------
        from vellum import Vellum

        client = Vellum(
            api_version="YOUR_API_VERSION",
            api_key="YOUR_API_KEY",
        )
        client.sandboxes.deploy_prompt(
            id="id",
            prompt_variant_id="prompt_variant_id",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            f"v1/sandboxes/{jsonable_encoder(id)}/prompts/{jsonable_encoder(prompt_variant_id)}/deploy",
            base_url=self._client_wrapper.get_environment().default,
            method="POST",
            json={
                "prompt_deployment_id": prompt_deployment_id,
                "prompt_deployment_name": prompt_deployment_name,
                "label": label,
                "release_tags": release_tags,
                "release_description": release_description,
            },
            headers={
                "content-type": "application/json",
            },
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    DeploymentRead,
                    parse_obj_as(
                        type_=DeploymentRead,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def upsert_sandbox_scenario(
        self,
        id: str,
        *,
        inputs: typing.Sequence[NamedScenarioInputRequest],
        label: typing.Optional[str] = OMIT,
        scenario_id: typing.Optional[str] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SandboxScenario:
        """
        Upserts a new scenario for a sandbox, keying off of the optionally provided scenario id.

        If an id is provided and has a match, the scenario will be updated. If no id is provided or no match
        is found, a new scenario will be appended to the end.

        Note that a full replacement of the scenario is performed, so any fields not provided will be removed
        or overwritten with default values.

        Parameters
        ----------
        id : str
            A UUID string identifying this sandbox.

        inputs : typing.Sequence[NamedScenarioInputRequest]
            The inputs for the scenario

        label : typing.Optional[str]

        scenario_id : typing.Optional[str]
            The id of the scenario to update. If none is provided, an id will be generated and a new scenario will be appended.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        SandboxScenario


        Examples
        --------
        from vellum import NamedScenarioInputStringVariableValueRequest, Vellum

        client = Vellum(
            api_version="YOUR_API_VERSION",
            api_key="YOUR_API_KEY",
        )
        client.sandboxes.upsert_sandbox_scenario(
            id="id",
            inputs=[
                NamedScenarioInputStringVariableValueRequest(
                    name="x",
                ),
                NamedScenarioInputStringVariableValueRequest(
                    name="x",
                ),
            ],
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            f"v1/sandboxes/{jsonable_encoder(id)}/scenarios",
            base_url=self._client_wrapper.get_environment().default,
            method="POST",
            json={
                "label": label,
                "inputs": convert_and_respect_annotation_metadata(
                    object_=inputs, annotation=typing.Sequence[NamedScenarioInputRequest], direction="write"
                ),
                "scenario_id": scenario_id,
            },
            headers={
                "content-type": "application/json",
            },
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    SandboxScenario,
                    parse_obj_as(
                        type_=SandboxScenario,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def delete_sandbox_scenario(
        self, id: str, scenario_id: str, *, request_options: typing.Optional[RequestOptions] = None
    ) -> None:
        """
        Deletes an existing scenario from a sandbox, keying off of the provided scenario id.

        Parameters
        ----------
        id : str
            A UUID string identifying this sandbox.

        scenario_id : str
            An id identifying the scenario that you'd like to delete

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        None

        Examples
        --------
        from vellum import Vellum

        client = Vellum(
            api_version="YOUR_API_VERSION",
            api_key="YOUR_API_KEY",
        )
        client.sandboxes.delete_sandbox_scenario(
            id="id",
            scenario_id="scenario_id",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            f"v1/sandboxes/{jsonable_encoder(id)}/scenarios/{jsonable_encoder(scenario_id)}",
            base_url=self._client_wrapper.get_environment().default,
            method="DELETE",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncSandboxesClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def deploy_prompt(
        self,
        id: str,
        prompt_variant_id: str,
        *,
        prompt_deployment_id: typing.Optional[str] = OMIT,
        prompt_deployment_name: typing.Optional[str] = OMIT,
        label: typing.Optional[str] = OMIT,
        release_tags: typing.Optional[typing.Sequence[str]] = OMIT,
        release_description: typing.Optional[str] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> DeploymentRead:
        """
        Parameters
        ----------
        id : str
            A UUID string identifying this sandbox.

        prompt_variant_id : str
            An ID identifying the Prompt you'd like to deploy.

        prompt_deployment_id : typing.Optional[str]
            The Vellum-generated ID of the Prompt Deployment you'd like to update. Cannot specify both this and prompt_deployment_name. Leave null to create a new Prompt Deployment.

        prompt_deployment_name : typing.Optional[str]
            The unique name of the Prompt Deployment you'd like to either create or update. Cannot specify both this and prompt_deployment_id. If provided and matches an existing Prompt Deployment, that Prompt Deployment will be updated. Otherwise, a new Prompt Deployment will be created.

        label : typing.Optional[str]
            In the event that a new Prompt Deployment is created, this will be the label it's given.

        release_tags : typing.Optional[typing.Sequence[str]]
            Optionally provide the release tags that you'd like to be associated with the latest release of the created/updated Prompt Deployment.

        release_description : typing.Optional[str]
            Optionally provide a description that details what's new in this Release.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        DeploymentRead


        Examples
        --------
        import asyncio

        from vellum import AsyncVellum

        client = AsyncVellum(
            api_version="YOUR_API_VERSION",
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.sandboxes.deploy_prompt(
                id="id",
                prompt_variant_id="prompt_variant_id",
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            f"v1/sandboxes/{jsonable_encoder(id)}/prompts/{jsonable_encoder(prompt_variant_id)}/deploy",
            base_url=self._client_wrapper.get_environment().default,
            method="POST",
            json={
                "prompt_deployment_id": prompt_deployment_id,
                "prompt_deployment_name": prompt_deployment_name,
                "label": label,
                "release_tags": release_tags,
                "release_description": release_description,
            },
            headers={
                "content-type": "application/json",
            },
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    DeploymentRead,
                    parse_obj_as(
                        type_=DeploymentRead,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def upsert_sandbox_scenario(
        self,
        id: str,
        *,
        inputs: typing.Sequence[NamedScenarioInputRequest],
        label: typing.Optional[str] = OMIT,
        scenario_id: typing.Optional[str] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SandboxScenario:
        """
        Upserts a new scenario for a sandbox, keying off of the optionally provided scenario id.

        If an id is provided and has a match, the scenario will be updated. If no id is provided or no match
        is found, a new scenario will be appended to the end.

        Note that a full replacement of the scenario is performed, so any fields not provided will be removed
        or overwritten with default values.

        Parameters
        ----------
        id : str
            A UUID string identifying this sandbox.

        inputs : typing.Sequence[NamedScenarioInputRequest]
            The inputs for the scenario

        label : typing.Optional[str]

        scenario_id : typing.Optional[str]
            The id of the scenario to update. If none is provided, an id will be generated and a new scenario will be appended.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        SandboxScenario


        Examples
        --------
        import asyncio

        from vellum import AsyncVellum, NamedScenarioInputStringVariableValueRequest

        client = AsyncVellum(
            api_version="YOUR_API_VERSION",
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.sandboxes.upsert_sandbox_scenario(
                id="id",
                inputs=[
                    NamedScenarioInputStringVariableValueRequest(
                        name="x",
                    ),
                    NamedScenarioInputStringVariableValueRequest(
                        name="x",
                    ),
                ],
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            f"v1/sandboxes/{jsonable_encoder(id)}/scenarios",
            base_url=self._client_wrapper.get_environment().default,
            method="POST",
            json={
                "label": label,
                "inputs": convert_and_respect_annotation_metadata(
                    object_=inputs, annotation=typing.Sequence[NamedScenarioInputRequest], direction="write"
                ),
                "scenario_id": scenario_id,
            },
            headers={
                "content-type": "application/json",
            },
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    SandboxScenario,
                    parse_obj_as(
                        type_=SandboxScenario,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def delete_sandbox_scenario(
        self, id: str, scenario_id: str, *, request_options: typing.Optional[RequestOptions] = None
    ) -> None:
        """
        Deletes an existing scenario from a sandbox, keying off of the provided scenario id.

        Parameters
        ----------
        id : str
            A UUID string identifying this sandbox.

        scenario_id : str
            An id identifying the scenario that you'd like to delete

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        None

        Examples
        --------
        import asyncio

        from vellum import AsyncVellum

        client = AsyncVellum(
            api_version="YOUR_API_VERSION",
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.sandboxes.delete_sandbox_scenario(
                id="id",
                scenario_id="scenario_id",
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            f"v1/sandboxes/{jsonable_encoder(id)}/scenarios/{jsonable_encoder(scenario_id)}",
            base_url=self._client_wrapper.get_environment().default,
            method="DELETE",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
