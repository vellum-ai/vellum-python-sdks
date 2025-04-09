# This file was auto-generated by Fern from our API Definition.

import typing
from ...core.client_wrapper import SyncClientWrapper
from .types.workflow_deployments_list_request_status import WorkflowDeploymentsListRequestStatus
from ...core.request_options import RequestOptions
from ...core.http_response import HttpResponse
from ...types.paginated_slim_workflow_deployment_list import PaginatedSlimWorkflowDeploymentList
from ...core.pydantic_utilities import parse_obj_as
from json.decoder import JSONDecodeError
from ...core.api_error import ApiError
from ...types.workflow_deployment_read import WorkflowDeploymentRead
from ...core.jsonable_encoder import jsonable_encoder
from ...types.workflow_deployment_event_executions_response import WorkflowDeploymentEventExecutionsResponse
from ...types.workflow_event_execution_read import WorkflowEventExecutionRead
from ...types.workflow_deployment_history_item import WorkflowDeploymentHistoryItem
from .types.list_workflow_release_tags_request_source import ListWorkflowReleaseTagsRequestSource
from ...types.paginated_workflow_release_tag_read_list import PaginatedWorkflowReleaseTagReadList
from ...types.workflow_release_tag_read import WorkflowReleaseTagRead
from ...core.client_wrapper import AsyncClientWrapper
from ...core.http_response import AsyncHttpResponse

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


class RawWorkflowDeploymentsClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def list(
        self,
        *,
        limit: typing.Optional[int] = None,
        offset: typing.Optional[int] = None,
        ordering: typing.Optional[str] = None,
        status: typing.Optional[WorkflowDeploymentsListRequestStatus] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> HttpResponse[PaginatedSlimWorkflowDeploymentList]:
        """
        Used to list all Workflow Deployments.

        Parameters
        ----------
        limit : typing.Optional[int]
            Number of results to return per page.

        offset : typing.Optional[int]
            The initial index from which to return the results.

        ordering : typing.Optional[str]
            Which field to use when ordering the results.

        status : typing.Optional[WorkflowDeploymentsListRequestStatus]
            status

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        HttpResponse[PaginatedSlimWorkflowDeploymentList]

        """
        _response = self._client_wrapper.httpx_client.request(
            "v1/workflow-deployments",
            base_url=self._client_wrapper.get_environment().base,
            method="GET",
            params={
                "limit": limit,
                "offset": offset,
                "ordering": ordering,
                "status": status,
            },
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                _data = typing.cast(
                    PaginatedSlimWorkflowDeploymentList,
                    parse_obj_as(
                        type_=PaginatedSlimWorkflowDeploymentList,  # type: ignore
                        object_=_response.json(),
                    ),
                )
                return HttpResponse(response=_response, data=_data)
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def retrieve(
        self, id: str, *, request_options: typing.Optional[RequestOptions] = None
    ) -> HttpResponse[WorkflowDeploymentRead]:
        """
        Used to retrieve a workflow deployment given its ID or name.

        Parameters
        ----------
        id : str
            Either the Workflow Deployment's ID or its unique name

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        HttpResponse[WorkflowDeploymentRead]

        """
        _response = self._client_wrapper.httpx_client.request(
            f"v1/workflow-deployments/{jsonable_encoder(id)}",
            base_url=self._client_wrapper.get_environment().base,
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                _data = typing.cast(
                    WorkflowDeploymentRead,
                    parse_obj_as(
                        type_=WorkflowDeploymentRead,  # type: ignore
                        object_=_response.json(),
                    ),
                )
                return HttpResponse(response=_response, data=_data)
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def list_workflow_deployment_event_executions(
        self,
        id: str,
        *,
        filters: typing.Optional[str] = None,
        limit: typing.Optional[int] = None,
        offset: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> HttpResponse[WorkflowDeploymentEventExecutionsResponse]:
        """
        Parameters
        ----------
        id : str

        filters : typing.Optional[str]

        limit : typing.Optional[int]
            Number of executions to return per page.

        offset : typing.Optional[int]
            The initial index from which to return the executions.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        HttpResponse[WorkflowDeploymentEventExecutionsResponse]

        """
        _response = self._client_wrapper.httpx_client.request(
            f"v1/workflow-deployments/{jsonable_encoder(id)}/execution-events",
            base_url=self._client_wrapper.get_environment().base,
            method="GET",
            params={
                "filters": filters,
                "limit": limit,
                "offset": offset,
            },
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                _data = typing.cast(
                    WorkflowDeploymentEventExecutionsResponse,
                    parse_obj_as(
                        type_=WorkflowDeploymentEventExecutionsResponse,  # type: ignore
                        object_=_response.json(),
                    ),
                )
                return HttpResponse(response=_response, data=_data)
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def workflow_deployment_event_execution(
        self, execution_id: str, id: str, *, request_options: typing.Optional[RequestOptions] = None
    ) -> HttpResponse[WorkflowEventExecutionRead]:
        """
        Parameters
        ----------
        execution_id : str

        id : str

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        HttpResponse[WorkflowEventExecutionRead]

        """
        _response = self._client_wrapper.httpx_client.request(
            f"v1/workflow-deployments/{jsonable_encoder(id)}/execution-events/{jsonable_encoder(execution_id)}",
            base_url=self._client_wrapper.get_environment().base,
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                _data = typing.cast(
                    WorkflowEventExecutionRead,
                    parse_obj_as(
                        type_=WorkflowEventExecutionRead,  # type: ignore
                        object_=_response.json(),
                    ),
                )
                return HttpResponse(response=_response, data=_data)
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def workflow_deployment_history_item_retrieve(
        self, history_id_or_release_tag: str, id: str, *, request_options: typing.Optional[RequestOptions] = None
    ) -> HttpResponse[WorkflowDeploymentHistoryItem]:
        """
        Retrieve a specific Workflow Deployment History Item by either its UUID or the name of a Release Tag that points to it.

        Parameters
        ----------
        history_id_or_release_tag : str
            Either the UUID of Workflow Deployment History Item you'd like to retrieve, or the name of a Release Tag that's pointing to the Workflow Deployment History Item you'd like to retrieve.

        id : str
            A UUID string identifying this workflow deployment.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        HttpResponse[WorkflowDeploymentHistoryItem]

        """
        _response = self._client_wrapper.httpx_client.request(
            f"v1/workflow-deployments/{jsonable_encoder(id)}/history/{jsonable_encoder(history_id_or_release_tag)}",
            base_url=self._client_wrapper.get_environment().base,
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                _data = typing.cast(
                    WorkflowDeploymentHistoryItem,
                    parse_obj_as(
                        type_=WorkflowDeploymentHistoryItem,  # type: ignore
                        object_=_response.json(),
                    ),
                )
                return HttpResponse(response=_response, data=_data)
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def list_workflow_release_tags(
        self,
        id: str,
        *,
        limit: typing.Optional[int] = None,
        offset: typing.Optional[int] = None,
        ordering: typing.Optional[str] = None,
        source: typing.Optional[ListWorkflowReleaseTagsRequestSource] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> HttpResponse[PaginatedWorkflowReleaseTagReadList]:
        """
        List Release Tags associated with the specified Workflow Deployment

        Parameters
        ----------
        id : str
            Either the Workflow Deployment's ID or its unique name

        limit : typing.Optional[int]
            Number of results to return per page.

        offset : typing.Optional[int]
            The initial index from which to return the results.

        ordering : typing.Optional[str]
            Which field to use when ordering the results.

        source : typing.Optional[ListWorkflowReleaseTagsRequestSource]

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        HttpResponse[PaginatedWorkflowReleaseTagReadList]

        """
        _response = self._client_wrapper.httpx_client.request(
            f"v1/workflow-deployments/{jsonable_encoder(id)}/release-tags",
            base_url=self._client_wrapper.get_environment().base,
            method="GET",
            params={
                "limit": limit,
                "offset": offset,
                "ordering": ordering,
                "source": source,
            },
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                _data = typing.cast(
                    PaginatedWorkflowReleaseTagReadList,
                    parse_obj_as(
                        type_=PaginatedWorkflowReleaseTagReadList,  # type: ignore
                        object_=_response.json(),
                    ),
                )
                return HttpResponse(response=_response, data=_data)
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def retrieve_workflow_release_tag(
        self, id: str, name: str, *, request_options: typing.Optional[RequestOptions] = None
    ) -> HttpResponse[WorkflowReleaseTagRead]:
        """
        Retrieve a Workflow Release Tag by tag name, associated with a specified Workflow Deployment.

        Parameters
        ----------
        id : str
            A UUID string identifying this workflow deployment.

        name : str
            The name of the Release Tag associated with this Workflow Deployment that you'd like to retrieve.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        HttpResponse[WorkflowReleaseTagRead]

        """
        _response = self._client_wrapper.httpx_client.request(
            f"v1/workflow-deployments/{jsonable_encoder(id)}/release-tags/{jsonable_encoder(name)}",
            base_url=self._client_wrapper.get_environment().base,
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                _data = typing.cast(
                    WorkflowReleaseTagRead,
                    parse_obj_as(
                        type_=WorkflowReleaseTagRead,  # type: ignore
                        object_=_response.json(),
                    ),
                )
                return HttpResponse(response=_response, data=_data)
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def update_workflow_release_tag(
        self,
        id: str,
        name: str,
        *,
        history_item_id: typing.Optional[str] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> HttpResponse[WorkflowReleaseTagRead]:
        """
        Updates an existing Release Tag associated with the specified Workflow Deployment.

        Parameters
        ----------
        id : str
            A UUID string identifying this workflow deployment.

        name : str
            The name of the Release Tag associated with this Workflow Deployment that you'd like to update.

        history_item_id : typing.Optional[str]
            The ID of the Workflow Deployment History Item to tag

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        HttpResponse[WorkflowReleaseTagRead]

        """
        _response = self._client_wrapper.httpx_client.request(
            f"v1/workflow-deployments/{jsonable_encoder(id)}/release-tags/{jsonable_encoder(name)}",
            base_url=self._client_wrapper.get_environment().base,
            method="PATCH",
            json={
                "history_item_id": history_item_id,
            },
            headers={
                "content-type": "application/json",
            },
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                _data = typing.cast(
                    WorkflowReleaseTagRead,
                    parse_obj_as(
                        type_=WorkflowReleaseTagRead,  # type: ignore
                        object_=_response.json(),
                    ),
                )
                return HttpResponse(response=_response, data=_data)
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncRawWorkflowDeploymentsClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def list(
        self,
        *,
        limit: typing.Optional[int] = None,
        offset: typing.Optional[int] = None,
        ordering: typing.Optional[str] = None,
        status: typing.Optional[WorkflowDeploymentsListRequestStatus] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncHttpResponse[PaginatedSlimWorkflowDeploymentList]:
        """
        Used to list all Workflow Deployments.

        Parameters
        ----------
        limit : typing.Optional[int]
            Number of results to return per page.

        offset : typing.Optional[int]
            The initial index from which to return the results.

        ordering : typing.Optional[str]
            Which field to use when ordering the results.

        status : typing.Optional[WorkflowDeploymentsListRequestStatus]
            status

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        AsyncHttpResponse[PaginatedSlimWorkflowDeploymentList]

        """
        _response = await self._client_wrapper.httpx_client.request(
            "v1/workflow-deployments",
            base_url=self._client_wrapper.get_environment().base,
            method="GET",
            params={
                "limit": limit,
                "offset": offset,
                "ordering": ordering,
                "status": status,
            },
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                _data = typing.cast(
                    PaginatedSlimWorkflowDeploymentList,
                    parse_obj_as(
                        type_=PaginatedSlimWorkflowDeploymentList,  # type: ignore
                        object_=_response.json(),
                    ),
                )
                return AsyncHttpResponse(response=_response, data=_data)
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def retrieve(
        self, id: str, *, request_options: typing.Optional[RequestOptions] = None
    ) -> AsyncHttpResponse[WorkflowDeploymentRead]:
        """
        Used to retrieve a workflow deployment given its ID or name.

        Parameters
        ----------
        id : str
            Either the Workflow Deployment's ID or its unique name

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        AsyncHttpResponse[WorkflowDeploymentRead]

        """
        _response = await self._client_wrapper.httpx_client.request(
            f"v1/workflow-deployments/{jsonable_encoder(id)}",
            base_url=self._client_wrapper.get_environment().base,
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                _data = typing.cast(
                    WorkflowDeploymentRead,
                    parse_obj_as(
                        type_=WorkflowDeploymentRead,  # type: ignore
                        object_=_response.json(),
                    ),
                )
                return AsyncHttpResponse(response=_response, data=_data)
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def list_workflow_deployment_event_executions(
        self,
        id: str,
        *,
        filters: typing.Optional[str] = None,
        limit: typing.Optional[int] = None,
        offset: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncHttpResponse[WorkflowDeploymentEventExecutionsResponse]:
        """
        Parameters
        ----------
        id : str

        filters : typing.Optional[str]

        limit : typing.Optional[int]
            Number of executions to return per page.

        offset : typing.Optional[int]
            The initial index from which to return the executions.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        AsyncHttpResponse[WorkflowDeploymentEventExecutionsResponse]

        """
        _response = await self._client_wrapper.httpx_client.request(
            f"v1/workflow-deployments/{jsonable_encoder(id)}/execution-events",
            base_url=self._client_wrapper.get_environment().base,
            method="GET",
            params={
                "filters": filters,
                "limit": limit,
                "offset": offset,
            },
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                _data = typing.cast(
                    WorkflowDeploymentEventExecutionsResponse,
                    parse_obj_as(
                        type_=WorkflowDeploymentEventExecutionsResponse,  # type: ignore
                        object_=_response.json(),
                    ),
                )
                return AsyncHttpResponse(response=_response, data=_data)
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def workflow_deployment_event_execution(
        self, execution_id: str, id: str, *, request_options: typing.Optional[RequestOptions] = None
    ) -> AsyncHttpResponse[WorkflowEventExecutionRead]:
        """
        Parameters
        ----------
        execution_id : str

        id : str

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        AsyncHttpResponse[WorkflowEventExecutionRead]

        """
        _response = await self._client_wrapper.httpx_client.request(
            f"v1/workflow-deployments/{jsonable_encoder(id)}/execution-events/{jsonable_encoder(execution_id)}",
            base_url=self._client_wrapper.get_environment().base,
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                _data = typing.cast(
                    WorkflowEventExecutionRead,
                    parse_obj_as(
                        type_=WorkflowEventExecutionRead,  # type: ignore
                        object_=_response.json(),
                    ),
                )
                return AsyncHttpResponse(response=_response, data=_data)
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def workflow_deployment_history_item_retrieve(
        self, history_id_or_release_tag: str, id: str, *, request_options: typing.Optional[RequestOptions] = None
    ) -> AsyncHttpResponse[WorkflowDeploymentHistoryItem]:
        """
        Retrieve a specific Workflow Deployment History Item by either its UUID or the name of a Release Tag that points to it.

        Parameters
        ----------
        history_id_or_release_tag : str
            Either the UUID of Workflow Deployment History Item you'd like to retrieve, or the name of a Release Tag that's pointing to the Workflow Deployment History Item you'd like to retrieve.

        id : str
            A UUID string identifying this workflow deployment.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        AsyncHttpResponse[WorkflowDeploymentHistoryItem]

        """
        _response = await self._client_wrapper.httpx_client.request(
            f"v1/workflow-deployments/{jsonable_encoder(id)}/history/{jsonable_encoder(history_id_or_release_tag)}",
            base_url=self._client_wrapper.get_environment().base,
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                _data = typing.cast(
                    WorkflowDeploymentHistoryItem,
                    parse_obj_as(
                        type_=WorkflowDeploymentHistoryItem,  # type: ignore
                        object_=_response.json(),
                    ),
                )
                return AsyncHttpResponse(response=_response, data=_data)
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def list_workflow_release_tags(
        self,
        id: str,
        *,
        limit: typing.Optional[int] = None,
        offset: typing.Optional[int] = None,
        ordering: typing.Optional[str] = None,
        source: typing.Optional[ListWorkflowReleaseTagsRequestSource] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncHttpResponse[PaginatedWorkflowReleaseTagReadList]:
        """
        List Release Tags associated with the specified Workflow Deployment

        Parameters
        ----------
        id : str
            Either the Workflow Deployment's ID or its unique name

        limit : typing.Optional[int]
            Number of results to return per page.

        offset : typing.Optional[int]
            The initial index from which to return the results.

        ordering : typing.Optional[str]
            Which field to use when ordering the results.

        source : typing.Optional[ListWorkflowReleaseTagsRequestSource]

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        AsyncHttpResponse[PaginatedWorkflowReleaseTagReadList]

        """
        _response = await self._client_wrapper.httpx_client.request(
            f"v1/workflow-deployments/{jsonable_encoder(id)}/release-tags",
            base_url=self._client_wrapper.get_environment().base,
            method="GET",
            params={
                "limit": limit,
                "offset": offset,
                "ordering": ordering,
                "source": source,
            },
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                _data = typing.cast(
                    PaginatedWorkflowReleaseTagReadList,
                    parse_obj_as(
                        type_=PaginatedWorkflowReleaseTagReadList,  # type: ignore
                        object_=_response.json(),
                    ),
                )
                return AsyncHttpResponse(response=_response, data=_data)
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def retrieve_workflow_release_tag(
        self, id: str, name: str, *, request_options: typing.Optional[RequestOptions] = None
    ) -> AsyncHttpResponse[WorkflowReleaseTagRead]:
        """
        Retrieve a Workflow Release Tag by tag name, associated with a specified Workflow Deployment.

        Parameters
        ----------
        id : str
            A UUID string identifying this workflow deployment.

        name : str
            The name of the Release Tag associated with this Workflow Deployment that you'd like to retrieve.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        AsyncHttpResponse[WorkflowReleaseTagRead]

        """
        _response = await self._client_wrapper.httpx_client.request(
            f"v1/workflow-deployments/{jsonable_encoder(id)}/release-tags/{jsonable_encoder(name)}",
            base_url=self._client_wrapper.get_environment().base,
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                _data = typing.cast(
                    WorkflowReleaseTagRead,
                    parse_obj_as(
                        type_=WorkflowReleaseTagRead,  # type: ignore
                        object_=_response.json(),
                    ),
                )
                return AsyncHttpResponse(response=_response, data=_data)
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def update_workflow_release_tag(
        self,
        id: str,
        name: str,
        *,
        history_item_id: typing.Optional[str] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncHttpResponse[WorkflowReleaseTagRead]:
        """
        Updates an existing Release Tag associated with the specified Workflow Deployment.

        Parameters
        ----------
        id : str
            A UUID string identifying this workflow deployment.

        name : str
            The name of the Release Tag associated with this Workflow Deployment that you'd like to update.

        history_item_id : typing.Optional[str]
            The ID of the Workflow Deployment History Item to tag

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        AsyncHttpResponse[WorkflowReleaseTagRead]

        """
        _response = await self._client_wrapper.httpx_client.request(
            f"v1/workflow-deployments/{jsonable_encoder(id)}/release-tags/{jsonable_encoder(name)}",
            base_url=self._client_wrapper.get_environment().base,
            method="PATCH",
            json={
                "history_item_id": history_item_id,
            },
            headers={
                "content-type": "application/json",
            },
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                _data = typing.cast(
                    WorkflowReleaseTagRead,
                    parse_obj_as(
                        type_=WorkflowReleaseTagRead,  # type: ignore
                        object_=_response.json(),
                    ),
                )
                return AsyncHttpResponse(response=_response, data=_data)
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
