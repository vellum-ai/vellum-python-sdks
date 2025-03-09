from collections import defaultdict
import logging
from queue import Empty, Queue
from threading import Thread
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from vellum.workflows.context import ExecutionContext, execution_context, get_execution_context
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.events.workflow import is_workflow_event
from vellum.workflows.exceptions import NodeException
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base_adornment_node import BaseAdornmentNode
from vellum.workflows.nodes.utils import create_adornment
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.references.output import OutputReference
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.types.generics import StateType
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

if TYPE_CHECKING:
    from vellum.workflows.events.workflow import WorkflowEvent

logger = logging.getLogger(__name__)

MapNodeItemType = TypeVar("MapNodeItemType")


class MapNode(BaseAdornmentNode[StateType], Generic[StateType, MapNodeItemType]):
    """
    Used to map over a list of items and execute a Subworkflow on each iteration.

    items: List[MapNodeItemType] - The items to map over
    max_concurrency: Optional[int] = None - The maximum number of concurrent subworkflow executions
    subworkflow: Type["BaseWorkflow"] - The Subworkflow to execute
    """

    items: List[MapNodeItemType]
    max_concurrency: Optional[int] = None

    class Outputs(BaseAdornmentNode.Outputs):
        pass

    class SubworkflowInputs(BaseInputs):
        # TODO: Both type: ignore's below are believed to be incorrect and both have the following error:
        # Type variable "workflows.nodes.map_node.map_node.MapNodeItemType" is unbound
        # https://app.shortcut.com/vellum/story/4118

        item: MapNodeItemType  # type: ignore[valid-type]
        index: int
        all_items: List[MapNodeItemType]  # type: ignore[valid-type]

    def run(self) -> Iterator[BaseOutput]:
        mapped_items: Dict[str, List] = defaultdict(list)
        for output_descripter in self.subworkflow.Outputs:
            mapped_items[output_descripter.name] = [None] * len(self.items)

        if not self.items:
            for output_name, output_list in mapped_items.items():
                yield BaseOutput(name=output_name, value=output_list)
            return

        self._event_queue: Queue[Tuple[int, WorkflowEvent]] = Queue()
        self._concurrency_queue: Queue[Thread] = Queue()
        fulfilled_iterations: List[bool] = []
        for index, item in enumerate(self.items):
            fulfilled_iterations.append(False)
            current_execution_context = get_execution_context()
            thread = Thread(
                target=self._context_run_subworkflow,
                kwargs={
                    "item": item,
                    "index": index,
                    "current_execution_context": current_execution_context,
                },
            )
            if self.max_concurrency is None:
                thread.start()
            else:
                self._concurrency_queue.put(thread)

        if self.max_concurrency is not None:
            concurrency_count = 0
            while concurrency_count < self.max_concurrency:
                is_empty = self._start_thread()
                if is_empty:
                    break

                concurrency_count += 1

        try:
            while map_node_event := self._event_queue.get():
                index = map_node_event[0]
                subworkflow_event = map_node_event[1]
                self._context._emit_subworkflow_event(subworkflow_event)

                if not is_workflow_event(subworkflow_event):
                    continue

                if subworkflow_event.workflow_definition != self.subworkflow:
                    continue

                if subworkflow_event.name == "workflow.execution.initiated":
                    for output_name in mapped_items.keys():
                        yield BaseOutput(name=output_name, delta=(None, index, "INITIATED"))

                elif subworkflow_event.name == "workflow.execution.fulfilled":
                    for output_reference, output_value in subworkflow_event.outputs:
                        if not isinstance(output_reference, OutputReference):
                            logger.error(
                                "Invalid key to map node's subworkflow event outputs",
                                extra={"output_reference_type": type(output_reference)},
                            )
                            continue

                        output_mapped_items = mapped_items[output_reference.name]
                        if index < 0 or index >= len(output_mapped_items):
                            logger.error(
                                "Invalid map node index", extra={"index": index, "output_name": output_reference.name}
                            )
                            continue

                        output_mapped_items[index] = output_value
                        yield BaseOutput(
                            name=output_reference.name,
                            delta=(output_value, index, "FULFILLED"),
                        )

                    fulfilled_iterations[index] = True
                    if all(fulfilled_iterations):
                        break

                    if self.max_concurrency is not None:
                        self._start_thread()
                elif subworkflow_event.name == "workflow.execution.paused":
                    raise NodeException(
                        code=WorkflowErrorCode.INVALID_OUTPUTS,
                        message=f"Subworkflow unexpectedly paused on iteration {index}",
                    )
                elif subworkflow_event.name == "workflow.execution.rejected":
                    raise NodeException(
                        f"Subworkflow failed on iteration {index} with error: {subworkflow_event.error.message}",
                        code=subworkflow_event.error.code,
                    )
        except Empty:
            pass

        for output_name, output_list in mapped_items.items():
            yield BaseOutput(name=output_name, value=output_list)

    def _context_run_subworkflow(
        self, *, item: MapNodeItemType, index: int, current_execution_context: ExecutionContext
    ) -> None:
        parent_context = current_execution_context.parent_context
        trace_id = current_execution_context.trace_id
        with execution_context(parent_context=parent_context, trace_id=trace_id):
            self._run_subworkflow(item=item, index=index)

    def _run_subworkflow(self, *, item: MapNodeItemType, index: int) -> None:
        context = WorkflowContext(vellum_client=self._context.vellum_client)
        subworkflow = self.subworkflow(
            parent_state=self.state,
            context=context,
        )
        events = subworkflow.stream(
            inputs=self.SubworkflowInputs(index=index, item=item, all_items=self.items),
            node_output_mocks=self._context._get_all_node_output_mocks(),
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
    def wrap(
        cls, items: List[MapNodeItemType], max_concurrency: Optional[int] = None
    ) -> Callable[..., Type["MapNode[StateType, MapNodeItemType]"]]: ...

    # TODO: We should be able to do this overload automatically as we do with node attributes
    # https://app.shortcut.com/vellum/story/5289
    @overload
    @classmethod
    def wrap(
        cls,
        items: BaseDescriptor[List[MapNodeItemType]],
        max_concurrency: Optional[int] = None,
    ) -> Callable[..., Type["MapNode[StateType, MapNodeItemType]"]]: ...

    @classmethod
    def wrap(
        cls,
        items: Union[List[MapNodeItemType], BaseDescriptor[List[MapNodeItemType]]],
        max_concurrency: Optional[int] = None,
    ) -> Callable[..., Type["MapNode[StateType, MapNodeItemType]"]]:
        return create_adornment(cls, attributes={"items": items, "max_concurrency": max_concurrency})

    @classmethod
    def __annotate_outputs_class__(cls, outputs_class: Type[BaseOutputs], reference: OutputReference) -> None:
        parameter_type = reference.types[0]
        annotation = List[parameter_type]  # type: ignore[valid-type]

        previous_annotations = {prev: annotation for prev in outputs_class.__annotations__ if not prev.startswith("_")}
        outputs_class.__annotations__ = {**previous_annotations, reference.name: annotation}
