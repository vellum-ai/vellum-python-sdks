import re
from typing import Callable, Dict, List, Optional, Set, Type

from mypy.nodes import (
    AssignmentStmt,
    CallExpr,
    ClassDef,
    Decorator,
    MemberExpr,
    NameExpr,
    OverloadedFuncDef,
    SymbolTableNode,
    TypeAlias as MypyTypeAlias,
    TypeInfo,
    Var,
)
from mypy.options import Options
from mypy.plugin import AttributeContext, ClassDefContext, FunctionSigContext, MethodContext, Plugin
from mypy.types import AnyType, CallableType, FunctionLike, Instance, Type as MypyType, TypeAliasType, UnionType

TypeResolver = Callable[[str, List[MypyType]], MypyType]
NODE_ATTRIBUTE_REGEX = r"^[a-z].*$"

DESCRIPTOR_PATHS: list[tuple[str, str, str]] = [
    (
        "vellum.workflows.outputs.base.BaseOutputs",
        "vellum.workflows.references.output.OutputReference",
        r"^[^_].*$",
    ),
    (
        "vellum.workflows.nodes.bases.base.BaseNode.ExternalInputs",
        "vellum.workflows.references.external_input.ExternalInputReference",
        r"^[^_].*$",
    ),
    (
        "vellum.workflows.nodes.bases.base.BaseNode.Execution",
        "vellum.workflows.references.execution_count.ExecutionCountReference",
        r"^count$",
    ),
    (
        "vellum.workflows.state.base.BaseState",
        "vellum.workflows.references.state_value.StateValueReference",
        r"^[^_].*$",
    ),
    (
        "vellum.workflows.inputs.base.BaseInputs",
        "vellum.workflows.references.workflow_input.WorkflowInputReference",
        r"^[^_].*$",
    ),
    (
        "vellum.workflows.nodes.bases.base.BaseNode",
        "vellum.workflows.references.node.NodeReference",
        NODE_ATTRIBUTE_REGEX,
    ),
]


def _is_subclass(type_info: Optional[TypeInfo], fullname: str) -> bool:
    if not type_info:
        return False

    if type_info.fullname == fullname:
        return True

    return any(base.type.fullname == fullname or _is_subclass(base.type, fullname) for base in type_info.bases)


def _get_attribute_mypy_type(type_info: TypeInfo, attribute_name: str) -> Optional[MypyType]:
    type_node = type_info.names.get(attribute_name)
    if type_node:
        return type_node.type

    bases = type_info.bases
    for base in bases:
        mypy_type = _get_attribute_mypy_type(base.type, attribute_name)
        if mypy_type:
            return mypy_type

    return None


class VellumMypyPlugin(Plugin):
    """
    This plugin is responsible for properly supporting types for all of the magic we
    do with Descriptors and this library in general.
    """

    def __init__(self, options: Options) -> None:
        """
        Mypy performs its analyses in two phases: semantic analysis and type checking.
        So we initialize state that we need to use across both phases here.

        - `_calls_with_nested_descriptor_expressions`: A set of instances that are defined
          within a BaseNode that reference a descriptor. Classes (e.g. Dataclasses) don't
          support Descriptors by default, so we first need to ensure we're in the context of
          a `BaseNode`, before then editing the signature to support Descriptors.

        - `_nested_descriptor_expressions`: A mapping of MemberExprs that point to a
          Descriptor to a callable that will resolve the type of the Descriptor. This field
          is used in combination with `_calls_with_nested_descriptor_expressions` to
          edit the signature of the function when a Descriptor is used as an argument.
        """

        self._calls_with_nested_descriptor_expressions: Set[CallExpr] = set()
        self._nested_descriptor_expressions: Dict[MemberExpr, TypeResolver] = {}

        super().__init__(options)

    def get_class_attribute_hook(self, fullname: str) -> Optional[Callable[[AttributeContext], MypyType]]:
        """
        This hook is used whenever we're accessing an attribute of a class. e.g. `MyClass.my_attribute`.

        We use it to replace all special class attribute references with our descriptors.

        TODO: We still need to support all other descriptors besides Outputs.
        https://app.shortcut.com/vellum/story/4768
        """
        return self._class_attribute_hook

    def _class_attribute_hook(self, ctx: AttributeContext) -> MypyType:
        if not isinstance(ctx.type, CallableType):
            return ctx.default_attr_type

        if not isinstance(ctx.type.ret_type, Instance):
            return ctx.default_attr_type

        if not isinstance(ctx.context, MemberExpr):
            return ctx.default_attr_type

        for base_path, descriptor_path, attribute_regex in DESCRIPTOR_PATHS:
            if not re.match(attribute_regex, ctx.context.name):
                continue

            if not _is_subclass(ctx.type.ret_type.type, base_path):
                continue

            symbol = ctx.type.ret_type.type.names.get(ctx.context.name)
            if symbol and isinstance(symbol.node, (Decorator, OverloadedFuncDef)):
                continue

            info = self.lookup_fully_qualified(descriptor_path)
            if info and isinstance(info.node, TypeInfo):
                return Instance(info.node, [self._resolve_descriptor_type(ctx.default_attr_type)])

        return ctx.default_attr_type

    def get_base_class_hook(self, fullname: str) -> Optional[Callable[[ClassDefContext], None]]:
        """
        This hook is used whenever we're defining a class. e.g. `class MyClass(BaseNode): ...`.

        We add support for any special Base Class we define in our project.
        """

        return self._base_class_hook

    def _base_class_hook(self, ctx: ClassDefContext) -> None:
        if _is_subclass(ctx.cls.info, "vellum.workflows.nodes.core.templating_node.node.TemplatingNode"):
            self._dynamic_output_node_class_hook(ctx, "result")
        elif _is_subclass(
            ctx.cls.info, "vellum.workflows.nodes.displayable.code_execution_node.node.CodeExecutionNode"
        ):
            self._dynamic_output_node_class_hook(ctx, "result")
        elif _is_subclass(ctx.cls.info, "vellum.workflows.nodes.displayable.final_output_node.node.FinalOutputNode"):
            self._dynamic_output_node_class_hook(ctx, "value")

        if _is_subclass(ctx.cls.info, "vellum.workflows.nodes.bases.base.BaseNode"):
            return self._base_node_class_hook(ctx)

        if _is_subclass(ctx.cls.info, "vellum.workflows.workflows.base.BaseWorkflow"):
            return self._base_workflow_class_hook(ctx)

        if _is_subclass(ctx.cls.info, "vellum.workflows.outputs.base.BaseOutputs"):
            return self._base_node_outputs_class_hook(ctx)

    def _dynamic_output_node_class_hook(self, ctx: ClassDefContext, attribute_name: str) -> None:
        """
        We use this hook to properly annotate the Outputs class for Templating Node and
        Code Execution Node using the resolved type
        of the TemplatingNode's and CodeExecutionNode's class _OutputType generic.
        """
        node_info = ctx.cls.info
        node_bases = ctx.cls.info.bases
        if not node_bases:
            return
        if not isinstance(node_bases[0], Instance):
            return

        base_args = node_bases[0].args
        base_node = node_bases[0].type

        if len(base_args) != 2:
            return

        base_node_resolved_type = base_args[1]
        if isinstance(base_node_resolved_type, AnyType):
            base_node_resolved_type = ctx.api.named_type("builtins.str")

        base_node_outputs = base_node.names.get("Outputs")
        if not base_node_outputs:
            return

        current_node_outputs = node_info.names.get("Outputs")
        if not current_node_outputs and isinstance(base_node_outputs.node, TypeInfo):
            node_info.names["Outputs"] = base_node_outputs.copy()

            new_outputs_fullname = f"{node_info.fullname}.Outputs"
            new_outputs_defn_raw = base_node_outputs.node.defn.serialize()
            new_outputs_defn_raw["fullname"] = new_outputs_fullname
            new_outputs_defn = ClassDef.deserialize(new_outputs_defn_raw)
            new_outputs_sym = TypeInfo(
                names=base_node_outputs.node.names.copy(),
                defn=new_outputs_defn,
                module_name=node_info.module_name,
            )

            base_result_sym = base_node_outputs.node.names[attribute_name].node
            if isinstance(base_result_sym, Var):
                new_result_sym = Var.deserialize(base_result_sym.serialize())
                new_result_sym._fullname = f"{new_outputs_fullname}.{attribute_name}"
                new_result_sym.type = base_node_resolved_type
                new_outputs_sym.names[attribute_name].node = new_result_sym
                new_outputs_sym.bases.append(Instance(base_node_outputs.node, []))
                node_info.names["Outputs"].node = new_outputs_sym

    def _base_node_class_hook(self, ctx: ClassDefContext) -> None:
        """
        Special handling of BaseNode class definitions
        """
        self._redefine_class_attributes_with_descriptors(ctx)

    def _base_node_outputs_class_hook(self, ctx: ClassDefContext) -> None:
        """
        Special handling of BaseNode.Outputs class definitions
        """
        self._redefine_class_attributes_with_descriptors(ctx)

    def _redefine_class_attributes_with_descriptors(self, ctx: ClassDefContext) -> None:
        """
        Given a class definition, we want to redefine all of the class attributes to accept both
        the original defined type, and the descriptor version of the type.
        """

        for key, sym in ctx.cls.info.names.items():
            if not isinstance(sym.node, Var):
                continue

            if not re.match(NODE_ATTRIBUTE_REGEX, key):
                continue

            type_ = sym.node.type
            if not type_:
                continue
            sym.node.type = self._get_resolvable_type(
                lambda fullname, types: ctx.api.named_type(fullname, types), type_
            )

        # Supports descriptors assigned to nested classes
        type_resolver = lambda fullname, types: ctx.api.named_type(fullname, types)  # noqa: E731
        for assignment in ctx.cls.defs.body:
            if not isinstance(assignment, AssignmentStmt):
                continue

            call_expr = assignment.rvalue
            if not isinstance(call_expr, CallExpr):
                continue

            self._collect_descriptor_expressions(type_resolver, call_expr)

    def _collect_descriptor_expressions(self, type_resolver: TypeResolver, call_expr: CallExpr) -> None:
        for arg in call_expr.args:
            if isinstance(arg, CallExpr):
                self._collect_descriptor_expressions(type_resolver, arg)
                continue

            if not isinstance(arg, MemberExpr):
                continue

            is_arg_registered = False
            for base_path, _, attribute_regex in DESCRIPTOR_PATHS:
                if not re.match(attribute_regex, arg.name):
                    continue

                if not isinstance(arg.expr, (NameExpr, MemberExpr)):
                    continue

                if not isinstance(arg.expr.node, TypeInfo):
                    continue

                if not _is_subclass(arg.expr.node, base_path):
                    continue

                is_arg_registered = True
                self._calls_with_nested_descriptor_expressions.add(call_expr)
                self._nested_descriptor_expressions[arg] = type_resolver
                break

            if not is_arg_registered:
                # Need to check node outputs that are inherited
                if (
                    re.match(r"^[^_].*$", arg.name)
                    and isinstance(arg.expr, MemberExpr)
                    and isinstance(arg.expr.expr, NameExpr)
                    and isinstance(arg.expr.expr.node, TypeInfo)
                    and _is_subclass(arg.expr.expr.node, "vellum.workflows.nodes.bases.base.BaseNode")
                    and arg.expr.name == "Outputs"
                ):
                    self._calls_with_nested_descriptor_expressions.add(call_expr)
                    self._nested_descriptor_expressions[arg] = type_resolver

    def _base_workflow_class_hook(self, ctx: ClassDefContext) -> None:
        """
        Placeholder for any special type logic we want to add to the Workflow class.
        """

        pass

    def get_function_signature_hook(self, fullname: str) -> Optional[Callable[[FunctionSigContext], FunctionLike]]:
        """
        This hook is used whenever we're calling a function and are type checking the signature. e.g. `f(a, b)`.

        We use this to support nested objects that reference descriptors within a node. Class initialization
        counts as a function call in mypy, so we want to support nested descriptors assigned to class instances
        we don't control, like dataclasses.
        """

        return self._function_signature_hook

    def _function_signature_hook(self, ctx: FunctionSigContext) -> FunctionLike:
        if not isinstance(ctx.context, CallExpr):
            return ctx.default_signature

        if ctx.context not in self._calls_with_nested_descriptor_expressions:
            return ctx.default_signature

        old_arg_types = ctx.default_signature.arg_types
        old_arg_names = ctx.default_signature.arg_names
        old_arg_kinds = ctx.default_signature.arg_kinds
        new_arg_types = []

        new_arg_by_name = {
            arg_name: ctx.context.args[arg_index] for arg_index, arg_name in enumerate(ctx.context.arg_names)
        }

        should_copy_new_signature = False

        for arg_index, old_arg_type in enumerate(old_arg_types):
            if arg_index >= len(old_arg_kinds) or arg_index >= len(old_arg_names):
                new_arg_types.append(old_arg_type)
                continue

            old_arg_kind = old_arg_kinds[arg_index]
            if old_arg_kind.is_named():
                old_arg_name = old_arg_names[arg_index]
                old_arg = new_arg_by_name.get(old_arg_name)
            elif arg_index < len(ctx.context.args):
                old_arg = ctx.context.args[arg_index]
            else:
                old_arg = None

            if isinstance(old_arg, MemberExpr) and old_arg in self._nested_descriptor_expressions:
                should_copy_new_signature = True

                new_arg_types.append(
                    self._get_resolvable_type(
                        self._nested_descriptor_expressions[old_arg],
                        old_arg_type,
                    )
                )
            else:
                new_arg_types.append(old_arg_type)

        if not should_copy_new_signature:
            return ctx.default_signature

        return ctx.default_signature.copy_modified(
            ret_type=ctx.default_signature.ret_type,
            arg_types=new_arg_types,
        )

    def _get_resolvable_type(
        self, get_named_type: Callable[[str, List[MypyType]], MypyType], type_: MypyType
    ) -> MypyType:
        if isinstance(type_, TypeAliasType) and type_.alias:
            if type_.alias.fullname == "vellum.workflows.types.core.Json":
                """
                We want to avoid infinite recursion, so we just state that the descriptor can
                just reference `Json` directly instead of each of the members.
                """
                return UnionType(
                    [
                        type_,
                        get_named_type("vellum.workflows.descriptors.base.BaseDescriptor", [type_]),
                    ]
                )

            """
            Type Aliases expand to an actual type, so we want to keep drilling down.
            Example: Foo = str
            """
            return self._get_resolvable_type(get_named_type, type_.alias.target)

        if isinstance(type_, UnionType):
            """
            If a node attribute is referencing a union type, we want to accept a descriptor
            pointing to any of the individual members.
            """

            return UnionType([self._get_resolvable_type(get_named_type, t) for t in type_.items])

        if isinstance(type_, Instance) and type_.type.fullname == "builtins.dict":
            """
            If a node attribute is referencing a dict, we want to accept a descriptor pointing
            to the dict itself or any of the values it maps to.
            """

            key_type = type_.args[0]
            value_type = type_.args[1]
            return get_named_type(
                type_.type.fullname,
                [
                    key_type,
                    self._get_resolvable_type(get_named_type, value_type),
                ],
            )

        """
        Otherwise by default, we want to accept a descriptor pointing to the type itself.
        """
        return UnionType(
            [
                type_,
                get_named_type("vellum.workflows.descriptors.base.BaseDescriptor", [type_]),
            ]
        )

    def get_attribute_hook(self, fullname: str) -> Optional[Callable[[AttributeContext], MypyType]]:
        return self._attribute_hook

    def _attribute_hook(self, ctx: AttributeContext) -> MypyType:
        if not isinstance(ctx.context, MemberExpr):
            return ctx.default_attr_type
        if not isinstance(ctx.context.expr, NameExpr) or ctx.context.expr.name != "self":
            return ctx.default_attr_type

        # TODO: ensure that `self` is a BaseNode
        # https://app.shortcut.com/vellum/story/5531

        return self._resolve_descriptor_type(ctx.default_attr_type)

    def _resolve_descriptor_type(self, default_type: MypyType) -> MypyType:
        if not isinstance(default_type, UnionType):
            return default_type

        non_descriptor_items = [
            (
                item.args[0]
                if isinstance(item, Instance)
                and _is_subclass(item.type, "vellum.workflows.descriptors.base.BaseDescriptor")
                and len(item.args) > 0
                else item
            )
            for item in default_type.items
        ]

        new_items = list(set(non_descriptor_items))

        if len(new_items) == 0:
            return default_type

        if len(new_items) == 1:
            return new_items[0]

        return UnionType(
            items=new_items,
        )

    def get_method_hook(self, fullname: str) -> Optional[Callable[[MethodContext], MypyType]]:
        """
        This hook is used whenever we're calling a method from a class and are type checking the return type.
        We use this to support special return types from our classes that isn't supported by default due to
        the lack of nested class inheritance, among other python pitfalls.
        """

        if fullname.endswith(".run"):
            return self._run_method_hook

        if fullname.endswith(".stream"):
            return self._stream_method_hook

        return None

    def _run_method_hook(self, ctx: MethodContext) -> MypyType:
        """
        We use this to target:
        - `BaseWorkflow.run()`, so that the WorkflowExecutionFulfilledEvent is properly typed
           using the `Outputs` class defined on the user-defined subclass of `Workflow`.
        - `BaseNode.run()`, so that the `Outputs` class defined on the user-defined subclass of `Node`
          is properly typed.
        """

        if isinstance(ctx.default_return_type, TypeAliasType):
            return self._workflow_run_method_hook(ctx)

        if isinstance(ctx.default_return_type, Instance):
            return self._node_run_method_hook(ctx)

        return ctx.default_return_type

    def _workflow_run_method_hook(self, ctx: MethodContext) -> MypyType:
        if not isinstance(ctx.default_return_type, TypeAliasType):
            return ctx.default_return_type

        alias = ctx.default_return_type.alias
        if not alias:
            return ctx.default_return_type

        alias_target = alias.target
        if not isinstance(alias_target, UnionType) or not alias_target.items:
            return ctx.default_return_type

        fulfilled_event = alias_target.items[0]
        if not isinstance(fulfilled_event, Instance):
            return ctx.default_return_type

        if fulfilled_event.type.fullname != "vellum.workflows.events.workflow.WorkflowExecutionFulfilledEvent":
            return ctx.default_return_type

        outputs_node = self._get_workflow_outputs_type_info(ctx)
        if not outputs_node:
            return ctx.default_return_type

        new_fulfilled_event = fulfilled_event.copy_modified(args=(Instance(outputs_node, []),))
        return TypeAliasType(
            alias=MypyTypeAlias(
                target=UnionType(
                    items=[new_fulfilled_event] + alias_target.items[1:],
                ),
                fullname=alias.fullname,
                line=alias.line,
                column=alias.column,
            ),
            args=ctx.default_return_type.args,
            line=ctx.default_return_type.line,
            column=ctx.default_return_type.column,
        )

    def _node_run_method_hook(self, ctx: MethodContext) -> MypyType:
        if not isinstance(ctx.default_return_type, Instance):
            return ctx.default_return_type

        if not _is_subclass(ctx.default_return_type.type, "vellum.workflows.nodes.bases.base.BaseNode.Outputs"):
            return ctx.default_return_type

        outputs_node = self._get_node_outputs_type_info(ctx)
        if not outputs_node:
            return ctx.default_return_type

        return Instance(outputs_node, [])

    def _stream_method_hook(self, ctx: MethodContext) -> MypyType:
        """
        We use this to target `Workflow.stream()` so that the WorkflowExecutionFulfilledEvent is properly typed
        using the `Outputs` class defined on the user-defined subclass of `Workflow`.
        """

        if not isinstance(ctx.default_return_type, TypeAliasType):
            return ctx.default_return_type

        alias = ctx.default_return_type.alias
        if not alias:
            return ctx.default_return_type

        alias_target = alias.target
        if (
            not isinstance(alias_target, Instance)
            or not _is_subclass(alias_target.type, "typing.Iterator")
            or not alias_target.args
        ):
            return ctx.default_return_type

        union_alias = alias_target.args[0]
        if not isinstance(union_alias, TypeAliasType) or not union_alias.alias:
            return ctx.default_return_type

        union_target = union_alias.alias.target
        if not isinstance(union_target, UnionType) or not union_target.items:
            return ctx.default_return_type

        fulfilled_event_index = -1
        fulfilled_event = None
        for event_type_index, event_type in enumerate(union_target.items):
            if not isinstance(event_type, Instance):
                continue

            if event_type.type.fullname != "vellum.workflows.events.workflow.WorkflowExecutionFulfilledEvent":
                continue

            fulfilled_event_index = event_type_index
            fulfilled_event = event_type

        if fulfilled_event_index == -1 or not fulfilled_event:
            return ctx.default_return_type

        outputs_node = self._get_workflow_outputs_type_info(ctx)
        if not outputs_node:
            return ctx.default_return_type

        new_fulfilled_event = fulfilled_event.copy_modified(args=(Instance(outputs_node, []),))
        return TypeAliasType(
            alias=MypyTypeAlias(
                target=alias_target.copy_modified(
                    args=[
                        TypeAliasType(
                            alias=MypyTypeAlias(
                                target=UnionType(
                                    items=[
                                        new_fulfilled_event if index == fulfilled_event_index else item
                                        for index, item in enumerate(union_target.items)
                                    ],
                                ),
                                fullname=union_alias.alias.fullname,
                                line=union_alias.alias.line,
                                column=union_alias.alias.column,
                            ),
                            args=union_alias.args,
                            line=union_alias.line,
                            column=union_alias.column,
                        )
                    ]
                    + list(alias_target.args[1:])
                ),
                fullname=alias.fullname,
                line=alias.line,
                column=alias.column,
            ),
            args=ctx.default_return_type.args,
            line=ctx.default_return_type.line,
            column=ctx.default_return_type.column,
        )

    def _get_workflow_outputs_type_info(self, ctx: MethodContext) -> Optional[TypeInfo]:
        if not isinstance(ctx.context, CallExpr):
            return None

        if not isinstance(ctx.context.callee, MemberExpr):
            return None

        expr = ctx.context.callee.expr
        instance = ctx.api.get_expression_type(expr)
        if not isinstance(instance, Instance) or not _is_subclass(
            instance.type, "vellum.workflows.workflows.base.BaseWorkflow"
        ):
            return None

        outputs_node = instance.type.names.get("Outputs")

        if (
            not outputs_node
            or not isinstance(outputs_node.node, TypeInfo)
            or not _is_subclass(outputs_node.node, "vellum.workflows.outputs.base.BaseOutputs")
        ):
            return None

        resolved_outputs_node = self._resolve_descriptors_in_outputs(outputs_node)

        if not isinstance(resolved_outputs_node.node, TypeInfo):
            return None

        return resolved_outputs_node.node

    def _get_node_outputs_type_info(self, ctx: MethodContext) -> Optional[TypeInfo]:
        if not isinstance(ctx.context, CallExpr):
            return None

        if not isinstance(ctx.context.callee, MemberExpr):
            return None

        expr = ctx.context.callee.expr
        instance = ctx.api.get_expression_type(expr)
        if not isinstance(instance, Instance) or not _is_subclass(
            instance.type, "vellum.workflows.nodes.bases.base.BaseNode"
        ):
            return None

        outputs_node = instance.type.names.get("Outputs")

        if (
            not outputs_node
            or not isinstance(outputs_node.node, TypeInfo)
            or not _is_subclass(outputs_node.node, "vellum.workflows.outputs.base.BaseOutputs")
        ):
            return None

        # TODO: For some reason, returning the correct Outputs type info is causing `result` to not
        # be found. `test_templating_node.py` is the best place to test this.
        # https://app.shortcut.com/vellum/story/6132
        # return outputs_node.node
        return None

    def _resolve_descriptors_in_outputs(self, type_info: SymbolTableNode) -> SymbolTableNode:
        new_type_info = type_info.copy()
        if not isinstance(new_type_info.node, TypeInfo):
            return new_type_info

        for sym in new_type_info.node.names.values():
            if isinstance(sym.node, Var):
                descriptor_type = sym.node.type
                if isinstance(descriptor_type, Instance) and _is_subclass(
                    descriptor_type.type, "vellum.workflows.descriptors.base.BaseDescriptor"
                ):
                    args = descriptor_type.args
                    if args:
                        sym.node.type = args[0]

        return new_type_info


def plugin(version: str) -> Type[VellumMypyPlugin]:
    return VellumMypyPlugin
