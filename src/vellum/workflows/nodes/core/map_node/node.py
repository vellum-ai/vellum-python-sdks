from collections import defaultdict
from queue import Empty, Queue
from threading import Thread
from typing import TYPE_CHECKING, Callable, Dict, Generic, List, Optional, Tuple, Type, TypeVar, Union, overload

from vellum.workflows.context import execution_context, get_parent_context
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.events.types import ParentContext
from vellum.workflows.exceptions import NodeException
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base_adornment_node import BaseAdornmentNode
from vellum.workflows.nodes.utils import create_adornment
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.references.output import OutputReference
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.types.generics import StateType
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

if TYPE_CHECKING:
    from vellum.workflows.events.workflow import WorkflowEvent

MapNodeItemType = TypeVar("MapNodeItemType")


class MapNode(BaseAdornmentNode[StateType], Generic[StateType, MapNodeItemType]):
    """
    Used to map over a list of items and execute a Subworkflow on each iteration.

    items: List[MapNodeItemType] - The items to map over
    subworkflow: Type["BaseWorkflow[SubworkflowInputs, BaseState]"] - The Subworkflow to execute on each iteration
    concurrency: Optional[int] = None - The maximum number of concurrent subworkflow executions
    """

    items: List[MapNodeItemType]
    concurrency: Optional[int] = None

    class Outputs(BaseAdornmentNode.Outputs):
        pass

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
        self._concurrency_queue: Queue[Thread] = Queue()
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
            if self.concurrency is None:
                thread.start()
            else:
                self._concurrency_queue.put(thread)

        if self.concurrency is not None:
            concurrency_count = 0
            while concurrency_count < self.concurrency:
                is_empty = self._start_thread()
                if is_empty:
                    break

                concurrency_count += 1

        try:
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

                    if self.concurrency is not None:
                        self._start_thread()
                elif terminal_event.name == "workflow.execution.paused":
                    raise NodeException(
                        code=WorkflowErrorCode.INVALID_OUTPUTS,
                        message=f"Subworkflow unexpectedly paused on iteration {index}",
                    )
                elif terminal_event.name == "workflow.execution.rejected":
                    raise NodeException(
                        f"Subworkflow failed on iteration {index} with error: {terminal_event.error.message}",
                        code=terminal_event.error.code,
                    )
        except Empty:
            pass

        outputs = self.Outputs()
        for output_name, output_list in mapped_items.items():
            setattr(outputs, output_name, output_list)

        return outputs

    def _context_run_subworkflow(
        self, *, item: MapNodeItemType, index: int, parent_context: Optional[ParentContext] = None
    ) -> None:
        parent_context = parent_context or self._context.parent_context
        with execution_context(parent_context=parent_context):
            self._run_subworkflow(item=item, index=index)

    def _run_subworkflow(self, *, item: MapNodeItemType, index: int) -> None:
        context = WorkflowContext(vellum_client=self._context.vellum_client)
        subworkflow = self.subworkflow(
            parent_state=self.state,
            context=context,
        )
        events = subworkflow.stream(
            inputs=self.SubworkflowInputs(index=index, item=item, all_items=self.items),
            event_filter=all_workflow_event_filter,
        )

        for event in events:
            self._event_queue.put((index, event))

    def _start_thread(self) -> bool:
        if self._concurrency_queue.empty():
            return False

        thread = self._concurrency_queue.get()
        thread.start()
        return True

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
        return create_adornment(cls, attributes={"items": items})

    @classmethod
    def __annotate_outputs_class__(cls, outputs_class: Type[BaseOutputs], reference: OutputReference) -> None:
        parameter_type = reference.types[0]
        annotation = List[parameter_type]  # type: ignore[valid-type]

        previous_annotations = {prev: annotation for prev in outputs_class.__annotations__ if not prev.startswith("_")}
        outputs_class.__annotations__ = {**previous_annotations, reference.name: annotation}
