# This file was auto-generated by Fern from our API Definition.

import typing
from ...core.client_wrapper import SyncClientWrapper
from .types.workflows_pull_request_format import WorkflowsPullRequestFormat
from ...core.request_options import RequestOptions
from ...core.jsonable_encoder import jsonable_encoder
from ...errors.bad_request_error import BadRequestError
from ...core.pydantic_utilities import parse_obj_as
from json.decoder import JSONDecodeError
from ...core.api_error import ApiError
from ...types.workflow_push_exec_config import WorkflowPushExecConfig
from ...types.workflow_push_deployment_config_request import WorkflowPushDeploymentConfigRequest
from ... import core
from ...types.workflow_push_response import WorkflowPushResponse
from ...core.client_wrapper import AsyncClientWrapper

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


class WorkflowsClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def pull(
        self,
        id: str,
        *,
        exclude_code: typing.Optional[bool] = None,
        format: typing.Optional[WorkflowsPullRequestFormat] = None,
        include_json: typing.Optional[bool] = None,
        include_sandbox: typing.Optional[bool] = None,
        strict: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Iterator[bytes]:
        """
        Parameters
        ----------
        id : str
            The ID of the Workflow to pull from

        exclude_code : typing.Optional[bool]

        format : typing.Optional[WorkflowsPullRequestFormat]

        include_json : typing.Optional[bool]

        include_sandbox : typing.Optional[bool]

        strict : typing.Optional[bool]

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration. You can pass in configuration such as `chunk_size`, and more to customize the request and response.

        Yields
        ------
        typing.Iterator[bytes]

        """
        with self._client_wrapper.httpx_client.stream(
            f"v1/workflows/{jsonable_encoder(id)}/pull",
            base_url=self._client_wrapper.get_environment().default,
            method="GET",
            params={
                "exclude_code": exclude_code,
                "format": format,
                "include_json": include_json,
                "include_sandbox": include_sandbox,
                "strict": strict,
            },
            request_options=request_options,
        ) as _response:
            try:
                if 200 <= _response.status_code < 300:
                    _chunk_size = request_options.get("chunk_size", None) if request_options is not None else None
                    for _chunk in _response.iter_bytes(chunk_size=_chunk_size):
                        yield _chunk
                    return
                _response.read()
                if _response.status_code == 400:
                    raise BadRequestError(
                        typing.cast(
                            typing.Optional[typing.Any],
                            parse_obj_as(
                                type_=typing.Optional[typing.Any],  # type: ignore
                                object_=_response.json(),
                            ),
                        )
                    )
                _response_json = _response.json()
            except JSONDecodeError:
                raise ApiError(status_code=_response.status_code, body=_response.text)
            raise ApiError(status_code=_response.status_code, body=_response_json)

    def push(
        self,
        *,
        exec_config: WorkflowPushExecConfig,
        workflow_sandbox_id: typing.Optional[str] = OMIT,
        deployment_config: typing.Optional[WorkflowPushDeploymentConfigRequest] = OMIT,
        artifact: typing.Optional[core.File] = OMIT,
        dry_run: typing.Optional[bool] = OMIT,
        strict: typing.Optional[bool] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> WorkflowPushResponse:
        """
        Parameters
        ----------
        exec_config : WorkflowPushExecConfig
            The execution configuration of the workflow.

        workflow_sandbox_id : typing.Optional[str]

        deployment_config : typing.Optional[WorkflowPushDeploymentConfigRequest]

        artifact : typing.Optional[core.File]
            See core.File for more documentation

        dry_run : typing.Optional[bool]

        strict : typing.Optional[bool]

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        WorkflowPushResponse


        Examples
        --------
        from vellum import Vellum

        client = Vellum(
            api_key="YOUR_API_KEY",
        )
        client.workflows.push(
            exec_config="exec_config",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            "v1/workflows/push",
            base_url=self._client_wrapper.get_environment().default,
            method="POST",
            data={
                "exec_config": exec_config,
                "workflow_sandbox_id": workflow_sandbox_id,
                "deployment_config": deployment_config,
                "dry_run": dry_run,
                "strict": strict,
            },
            files={
                "artifact": artifact,
            },
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    WorkflowPushResponse,
                    parse_obj_as(
                        type_=WorkflowPushResponse,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncWorkflowsClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def pull(
        self,
        id: str,
        *,
        exclude_code: typing.Optional[bool] = None,
        format: typing.Optional[WorkflowsPullRequestFormat] = None,
        include_json: typing.Optional[bool] = None,
        include_sandbox: typing.Optional[bool] = None,
        strict: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.AsyncIterator[bytes]:
        """
        Parameters
        ----------
        id : str
            The ID of the Workflow to pull from

        exclude_code : typing.Optional[bool]

        format : typing.Optional[WorkflowsPullRequestFormat]

        include_json : typing.Optional[bool]

        include_sandbox : typing.Optional[bool]

        strict : typing.Optional[bool]

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration. You can pass in configuration such as `chunk_size`, and more to customize the request and response.

        Yields
        ------
        typing.AsyncIterator[bytes]

        """
        async with self._client_wrapper.httpx_client.stream(
            f"v1/workflows/{jsonable_encoder(id)}/pull",
            base_url=self._client_wrapper.get_environment().default,
            method="GET",
            params={
                "exclude_code": exclude_code,
                "format": format,
                "include_json": include_json,
                "include_sandbox": include_sandbox,
                "strict": strict,
            },
            request_options=request_options,
        ) as _response:
            try:
                if 200 <= _response.status_code < 300:
                    _chunk_size = request_options.get("chunk_size", None) if request_options is not None else None
                    async for _chunk in _response.aiter_bytes(chunk_size=_chunk_size):
                        yield _chunk
                    return
                await _response.aread()
                if _response.status_code == 400:
                    raise BadRequestError(
                        typing.cast(
                            typing.Optional[typing.Any],
                            parse_obj_as(
                                type_=typing.Optional[typing.Any],  # type: ignore
                                object_=_response.json(),
                            ),
                        )
                    )
                _response_json = _response.json()
            except JSONDecodeError:
                raise ApiError(status_code=_response.status_code, body=_response.text)
            raise ApiError(status_code=_response.status_code, body=_response_json)

    async def push(
        self,
        *,
        exec_config: WorkflowPushExecConfig,
        workflow_sandbox_id: typing.Optional[str] = OMIT,
        deployment_config: typing.Optional[WorkflowPushDeploymentConfigRequest] = OMIT,
        artifact: typing.Optional[core.File] = OMIT,
        dry_run: typing.Optional[bool] = OMIT,
        strict: typing.Optional[bool] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> WorkflowPushResponse:
        """
        Parameters
        ----------
        exec_config : WorkflowPushExecConfig
            The execution configuration of the workflow.

        workflow_sandbox_id : typing.Optional[str]

        deployment_config : typing.Optional[WorkflowPushDeploymentConfigRequest]

        artifact : typing.Optional[core.File]
            See core.File for more documentation

        dry_run : typing.Optional[bool]

        strict : typing.Optional[bool]

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        WorkflowPushResponse


        Examples
        --------
        import asyncio

        from vellum import AsyncVellum

        client = AsyncVellum(
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.workflows.push(
                exec_config="exec_config",
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            "v1/workflows/push",
            base_url=self._client_wrapper.get_environment().default,
            method="POST",
            data={
                "exec_config": exec_config,
                "workflow_sandbox_id": workflow_sandbox_id,
                "deployment_config": deployment_config,
                "dry_run": dry_run,
                "strict": strict,
            },
            files={
                "artifact": artifact,
            },
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    WorkflowPushResponse,
                    parse_obj_as(
                        type_=WorkflowPushResponse,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
