# This file was auto-generated by Fern from our API Definition.

import typing
from ...core.client_wrapper import SyncClientWrapper
from .raw_client import RawSandboxesClient
from ...core.request_options import RequestOptions
from ...types.deployment_read import DeploymentRead
from ...types.named_scenario_input_request import NamedScenarioInputRequest
from ...types.sandbox_scenario import SandboxScenario
from ...core.client_wrapper import AsyncClientWrapper
from .raw_client import AsyncRawSandboxesClient

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


class SandboxesClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._raw_client = RawSandboxesClient(client_wrapper=client_wrapper)

    @property
    def with_raw_response(self) -> RawSandboxesClient:
        """
        Retrieves a raw implementation of this client that returns raw responses.

        Returns
        -------
        RawSandboxesClient
        """
        return self._raw_client

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
            api_key="YOUR_API_KEY",
        )
        client.sandboxes.deploy_prompt(
            id="id",
            prompt_variant_id="prompt_variant_id",
        )
        """
        response = self._raw_client.deploy_prompt(
            id,
            prompt_variant_id,
            prompt_deployment_id=prompt_deployment_id,
            prompt_deployment_name=prompt_deployment_name,
            label=label,
            release_tags=release_tags,
            release_description=release_description,
            request_options=request_options,
        )
        return response.data

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
            api_key="YOUR_API_KEY",
        )
        client.sandboxes.upsert_sandbox_scenario(
            id="id",
            label="Scenario 1",
            inputs=[
                NamedScenarioInputStringVariableValueRequest(
                    value="Hello, world!",
                    name="var_1",
                ),
                NamedScenarioInputStringVariableValueRequest(
                    value="Why hello, there!",
                    name="var_2",
                ),
            ],
        )
        """
        response = self._raw_client.upsert_sandbox_scenario(
            id,
            inputs=inputs,
            label=label,
            scenario_id=scenario_id,
            request_options=request_options,
        )
        return response.data

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
            api_key="YOUR_API_KEY",
        )
        client.sandboxes.delete_sandbox_scenario(
            id="id",
            scenario_id="scenario_id",
        )
        """
        response = self._raw_client.delete_sandbox_scenario(
            id,
            scenario_id,
            request_options=request_options,
        )
        return response.data


class AsyncSandboxesClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._raw_client = AsyncRawSandboxesClient(client_wrapper=client_wrapper)

    @property
    def with_raw_response(self) -> AsyncRawSandboxesClient:
        """
        Retrieves a raw implementation of this client that returns raw responses.

        Returns
        -------
        AsyncRawSandboxesClient
        """
        return self._raw_client

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
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.sandboxes.deploy_prompt(
                id="id",
                prompt_variant_id="prompt_variant_id",
            )


        asyncio.run(main())
        """
        response = await self._raw_client.deploy_prompt(
            id,
            prompt_variant_id,
            prompt_deployment_id=prompt_deployment_id,
            prompt_deployment_name=prompt_deployment_name,
            label=label,
            release_tags=release_tags,
            release_description=release_description,
            request_options=request_options,
        )
        return response.data

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
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.sandboxes.upsert_sandbox_scenario(
                id="id",
                label="Scenario 1",
                inputs=[
                    NamedScenarioInputStringVariableValueRequest(
                        value="Hello, world!",
                        name="var_1",
                    ),
                    NamedScenarioInputStringVariableValueRequest(
                        value="Why hello, there!",
                        name="var_2",
                    ),
                ],
            )


        asyncio.run(main())
        """
        response = await self._raw_client.upsert_sandbox_scenario(
            id,
            inputs=inputs,
            label=label,
            scenario_id=scenario_id,
            request_options=request_options,
        )
        return response.data

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
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.sandboxes.delete_sandbox_scenario(
                id="id",
                scenario_id="scenario_id",
            )


        asyncio.run(main())
        """
        response = await self._raw_client.delete_sandbox_scenario(
            id,
            scenario_id,
            request_options=request_options,
        )
        return response.data
