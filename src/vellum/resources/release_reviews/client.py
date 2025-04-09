# This file was auto-generated by Fern from our API Definition.

from ...core.client_wrapper import SyncClientWrapper
import typing
from ...core.request_options import RequestOptions
from ...types.workflow_deployment_release import WorkflowDeploymentRelease
from ...core.jsonable_encoder import jsonable_encoder
from ...core.pydantic_utilities import parse_obj_as
from json.decoder import JSONDecodeError
from ...core.api_error import ApiError
from ...core.client_wrapper import AsyncClientWrapper


class ReleaseReviewsClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def retrieve_workflow_deployment_release(
        self, id: str, release_id_or_release_tag: str, *, request_options: typing.Optional[RequestOptions] = None
    ) -> WorkflowDeploymentRelease:
        """
        Retrieve a specific Workflow Deployment Release by either its UUID or the name of a Release Tag that points to it.

        Parameters
        ----------
        id : str
            A UUID string identifying this workflow deployment.

        release_id_or_release_tag : str
            Either the UUID of Workflow Deployment Release you'd like to retrieve, or the name of a Release Tag that's pointing to the Workflow Deployment Release you'd like to retrieve.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        WorkflowDeploymentRelease


        Examples
        --------
        from vellum import Vellum

        client = Vellum(
            api_key="YOUR_API_KEY",
        )
        client.release_reviews.retrieve_workflow_deployment_release(
            id="id",
            release_id_or_release_tag="release_id_or_release_tag",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            f"v1/workflow-deployments/{jsonable_encoder(id)}/releases/{jsonable_encoder(release_id_or_release_tag)}",
            base_url=self._client_wrapper.get_environment().base,
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    WorkflowDeploymentRelease,
                    parse_obj_as(
                        type_=WorkflowDeploymentRelease,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncReleaseReviewsClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def retrieve_workflow_deployment_release(
        self, id: str, release_id_or_release_tag: str, *, request_options: typing.Optional[RequestOptions] = None
    ) -> WorkflowDeploymentRelease:
        """
        Retrieve a specific Workflow Deployment Release by either its UUID or the name of a Release Tag that points to it.

        Parameters
        ----------
        id : str
            A UUID string identifying this workflow deployment.

        release_id_or_release_tag : str
            Either the UUID of Workflow Deployment Release you'd like to retrieve, or the name of a Release Tag that's pointing to the Workflow Deployment Release you'd like to retrieve.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        WorkflowDeploymentRelease


        Examples
        --------
        import asyncio

        from vellum import AsyncVellum

        client = AsyncVellum(
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.release_reviews.retrieve_workflow_deployment_release(
                id="id",
                release_id_or_release_tag="release_id_or_release_tag",
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            f"v1/workflow-deployments/{jsonable_encoder(id)}/releases/{jsonable_encoder(release_id_or_release_tag)}",
            base_url=self._client_wrapper.get_environment().base,
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    WorkflowDeploymentRelease,
                    parse_obj_as(
                        type_=WorkflowDeploymentRelease,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
