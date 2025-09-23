"""Placeholder integrations client until official SDK support lands."""

import typing

from ...core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ...core.request_options import RequestOptions


class IntegrationsClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def retrieve_integration_tool_definition(
        self,
        *,
        provider: str,
        integration: str,
        tool_name: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """Retrieve metadata for an integration tool.

        TODO(vellum): Replace this stub with the official SDK call once the
        integrations endpoints are published. The intended flow is:

        ```python
        # return client.integrations.retrieve_integration_tool_definition(
        #     provider=provider,
        #     integration=integration,
        #     tool_name=tool_name,
        #     request_options=request_options,
        # )
        ```
        """

        raise NotImplementedError(
            "The integrations client no longer performs raw HTTP requests. "
            "Update to the official Vellum SDK integrations endpoints once available."
        )

    def execute_integration_tool(
        self,
        *,
        provider: str,
        integration: str,
        tool_name: str,
        arguments: typing.Dict[str, typing.Optional[typing.Any]],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """Execute an integration tool.

        TODO(vellum): Replace this stub with the official SDK call once the
        integrations endpoints are published. The intended flow is:

        ```python
        # return client.integrations.execute_integration_tool(
        #     provider=provider,
        #     integration=integration,
        #     tool_name=tool_name,
        #     arguments=arguments,
        #     request_options=request_options,
        # )
        ```
        """

        raise NotImplementedError(
            "The integrations client no longer performs raw HTTP requests. "
            "Update to the official Vellum SDK integrations endpoints once available."
        )


class AsyncIntegrationsClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def retrieve_integration_tool_definition(
        self,
        *,
        provider: str,
        integration: str,
        tool_name: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """Async variant of retrieve_integration_tool_definition stub."""

        raise NotImplementedError(
            "The async integrations client no longer performs raw HTTP requests. "
            "Update to the official Vellum SDK integrations endpoints once available."
        )

    async def execute_integration_tool(
        self,
        *,
        provider: str,
        integration: str,
        tool_name: str,
        arguments: typing.Dict[str, typing.Optional[typing.Any]],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """Async variant of execute_integration_tool stub."""

        raise NotImplementedError(
            "The async integrations client no longer performs raw HTTP requests. "
            "Update to the official Vellum SDK integrations endpoints once available."
        )
