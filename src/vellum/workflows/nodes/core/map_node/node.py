from collections import defaultdict
from queue import Empty, Queue
from threading import Thread
from typing import TYPE_CHECKING, Callable, Dict, Generic, List, Optional, Tuple, Type, TypeVar, Union, overload

from vellum.workflows.context import execution_context, get_parent_context
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.errors.types import VellumErrorCode
from vellum.workflows.events.types import ParentContext
from vellum.workflows.exceptions import NodeException
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.types.generics import NodeType, StateType
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

if TYPE_CHECKING:
    from vellum.workflows import BaseWorkflow
    from vellum.workflows.events.workflow import WorkflowEvent

MapNodeItemType = TypeVar("MapNodeItemType")


class MapNode(BaseNode, Generic[StateType, MapNodeItemType]):
    """
    Used to map over a list of items and execute a Subworkflow on each iteration.

    items: List[MapNodeItemType] - The items to map over
    subworkflow: Type["BaseWorkflow[SubworkflowInputs, BaseState]"] - The Subworkflow to execute on each iteration
    concurrency: Optional[int] = None - The maximum number of concurrent subworkflow executions
    """

    items: List[MapNodeItemType]
    subworkflow: Type["BaseWorkflow"]
    concurrency: Optional[int] = None

    class Outputs(BaseOutputs):
        mapped_items: list

    class SubworkflowInputs(BaseInputs):
        # TODO: Both type: ignore's below are believed to be incorrect and both have the following error:
        # Type variable "workflows.nodes.map_node.map_node.MapNodeItemType" is unbound
        # https://app.shortcut.com/vellum/story/4118

        item: MapNodeItemType  # type: ignore[valid-type]
        index: int
        all_items: List[MapNodeItemType]  # type: ignore[valid-type]

    def run(self) -> Outputs:
        mapped_items: Dict[str, List] = defaultdict(list)
        for output_descripter in self.subworkflow.Outputs:
            mapped_items[output_descripter.name] = [None] * len(self.items)

        self._event_queue: Queue[Tuple[int, WorkflowEvent]] = Queue()
        fulfilled_iterations: List[bool] = []
        for index, item in enumerate(self.items):
            fulfilled_iterations.append(False)
            parent_context = get_parent_context() or self._context.parent_context
            thread = Thread(
                target=self._context_run_subworkflow,
                kwargs={
                    "item": item,
                    "index": index,
                    "parent_context": parent_context,
                },
            )
            thread.start()

        try:
            # We should consolidate this logic with the logic workflow runner uses
            # https://app.shortcut.com/vellum/story/4736
            while map_node_event := self._event_queue.get():
                index = map_node_event[0]
                terminal_event = map_node_event[1]
                self._context._emit_subworkflow_event(terminal_event)

                if terminal_event.name == "workflow.execution.fulfilled":
                    workflow_output_vars = vars(terminal_event.outputs)

                    for output_name in workflow_output_vars:
                        output_mapped_items = mapped_items[output_name]
                        output_mapped_items[index] = workflow_output_vars[output_name]

                    fulfilled_iterations[index] = True
                    if all(fulfilled_iterations):
                        break
                elif terminal_event.name == "workflow.execution.paused":
                    raise NodeException(
                        code=VellumErrorCode.INVALID_OUTPUTS,
                        message=f"Subworkflow unexpectedly paused on iteration {index}",
                    )
                elif terminal_event.name == "workflow.execution.rejected":
                    raise NodeException(
                        f"Subworkflow failed on iteration {index} with error: {terminal_event.error.message}",
                        code=terminal_event.error.code,
                    )
        except Empty:
            pass
        return self.Outputs(**mapped_items)

    def _context_run_subworkflow(
        self, *, item: MapNodeItemType, index: int, parent_context: Optional[ParentContext] = None
    ) -> None:
        parent_context = parent_context or self._context.parent_context
        with execution_context(parent_context=parent_context):
            self._run_subworkflow(item=item, index=index)

    def _run_subworkflow(self, *, item: MapNodeItemType, index: int) -> None:
        context = WorkflowContext(_vellum_client=self._context._vellum_client)
        subworkflow = self.subworkflow(parent_state=self.state, context=context)
        events = subworkflow.stream(
            inputs=self.SubworkflowInputs(index=index, item=item, all_items=self.items),
            event_filter=all_workflow_event_filter,
        )

        for event in events:
            self._event_queue.put((index, event))

    @overload
    @classmethod
    def wrap(cls, items: List[MapNodeItemType]) -> Callable[..., Type["MapNode[StateType, MapNodeItemType]"]]: ...

    # TODO: We should be able to do this overload automatically as we do with node attributes
    # https://app.shortcut.com/vellum/story/5289
    @overload
    @classmethod
    def wrap(
        cls, items: BaseDescriptor[List[MapNodeItemType]]
    ) -> Callable[..., Type["MapNode[StateType, MapNodeItemType]"]]: ...

    @classmethod
    def wrap(
        cls, items: Union[List[MapNodeItemType], BaseDescriptor[List[MapNodeItemType]]]
    ) -> Callable[..., Type["MapNode[StateType, MapNodeItemType]"]]:
        _items = items

        def decorator(inner_cls: Type[NodeType]) -> Type["MapNode[StateType, MapNodeItemType]"]:
            # Investigate how to use dependency injection to avoid circular imports
            # https://app.shortcut.com/vellum/story/4116
            from vellum.workflows import BaseWorkflow

            class Subworkflow(BaseWorkflow[MapNode.SubworkflowInputs, BaseState]):
                graph = inner_cls

                # mypy is wrong here, this works and is defined
                class Outputs(inner_cls.Outputs):  # type: ignore[name-defined]
                    pass

            class WrappedNodeOutputs(BaseOutputs):
                pass

            WrappedNodeOutputs.__annotations__ = {
                # TODO: We'll need to infer the type T of Subworkflow.Outputs[name] so we could do List[T] here
                # https://app.shortcut.com/vellum/story/4119
                descriptor.name: List
                for descriptor in inner_cls.Outputs
            }

            class WrappedNode(MapNode[StateType, MapNodeItemType]):
                items = _items
                subworkflow = Subworkflow

                class Outputs(WrappedNodeOutputs):
                    pass

            return WrappedNode

        return decorator
