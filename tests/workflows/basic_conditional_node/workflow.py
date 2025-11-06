from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.displayable.conditional_node import ConditionalNode
from vellum.workflows.ports.port import Port
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class Inputs(BaseInputs):
    category: str


class QuestionPassthroughNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        question = Inputs.category


class ComplaintPassthroughNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        complaint = Inputs.category


class ComplimentPassthroughNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        compliment = Inputs.category


class StatementPassthroughNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        statement = Inputs.category


class FallthroughPassthroughNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        fallthrough = Inputs.category


class CategoryConditionalNode(ConditionalNode):
    class Ports(ConditionalNode.Ports):
        category_question = Port.on_if(Inputs.category.equals("question"))
        category_complaint = Port.on_elif(Inputs.category.equals("complaint"))
        category_compliment = Port.on_elif(Inputs.category.equals("compliment"))
        category_statement = Port.on_elif(
            Inputs.category.equals("statement")
            & (Inputs.category.equals("statement") & Inputs.category.equals("statement"))
        )
        category_fallthrough = Port.on_else()


class CategoryWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = {
        CategoryConditionalNode.Ports.category_question >> QuestionPassthroughNode,
        CategoryConditionalNode.Ports.category_complaint >> ComplaintPassthroughNode,
        CategoryConditionalNode.Ports.category_compliment >> ComplimentPassthroughNode,
        CategoryConditionalNode.Ports.category_statement >> StatementPassthroughNode,
        CategoryConditionalNode.Ports.category_fallthrough >> FallthroughPassthroughNode,
    }

    class Outputs(BaseWorkflow.Outputs):
        question = QuestionPassthroughNode.Outputs.question
        complaint = ComplaintPassthroughNode.Outputs.complaint
        compliment = ComplimentPassthroughNode.Outputs.compliment
        statement = StatementPassthroughNode.Outputs.statement
        fallthrough = FallthroughPassthroughNode.Outputs.fallthrough
