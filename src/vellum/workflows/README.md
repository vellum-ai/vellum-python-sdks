<p align="center">
  <h1 align="center">
  Vellum Workflows SDK
  </h1>
  <p align="center">
    <a href="https://docs.vellum.ai/developers/workflows-sdk">Learn more</a>
    ·
    <a href="https://www.vellum.ai/landing-pages/request-demo">Talk to us</a>
  </p>
</p>

# Introduction

The Vellum Workflows SDK is a framework for defining and executing complex AI systems as graphs.

The Vellum Workflows SDK provides a declarative python syntax for both defining and executing the control flow of graphs.
Unlike other graph execution frameworks, which are functional or event-driven in nature, Vellum's Workflows SDK defines the control flow of a graph
statically and makes use of strict typing. This means that the structure of the graph is known ahead of time, and you get all the benefits of type
safety and intellisense. This ultimately makes it easier to build more predictable and robust AI systems.

Unique amongst other frameworks, Vellum's Workflows SDK also allows you to _visualize, edit, and execute_ your graph in a UI, pushing and pulling changes from
code to UI and vice versa.


## Core Features
- **Nodes**: Nodes are the basic building blocks of a graph. They represent a single task or function that can be executed.
- **Graph Syntax**: An intuitive declarative syntax for defining the control flow of a graph.
- **Inputs and Outputs**: Both the Workflow itslef and individual Nodes can take in inputs and produce outputs, which can be used to pass information between nodes.
- **State**: Nodes can read and write to the graph's global state, which can be used to share information between nodes without defining explicit inputs and outputs.
- **Advanced Control Flow**: Support for looping, conditionals, paralellism, state forking, and more.
- **Streaming**: Nodes can stream output values back to the runner, allowing for long-running tasks like chat completions to return partial results.
- **Human-in-the-loop**: Nodes can wait for External Inputs, allowing for a pause in the Workflow until a human or external system provides input.
- **UI Integration**: Push and pull changes from code to Vellum's UI and vice versa, allowing for rapid testing and iteration.

## Quickstart

1. Install the Vellum Workflows SDK:

    ```bash
    pip install vellum-ai
    ```

2. Import the Vellum Workflows SDK and define your first Workflow:

    ```python
    # my_workflow.py

    from workflows import BaseWorkflow
    from workflows.nodes import BaseNode


    class MyNode(BaseNode):

        class Outputs(BaseNode.Outputs):
            result: str

        def run(self):
            return self.Outputs(result="Hello, World!")


    class MyWorkflow(BaseWorkflow):
        graph = MyNode

        class Outputs(BaseWorkflow.Outputs):
            result = MyNode.Outputs.result


    if __name__ == "__main__":
        workflow = MyWorkflow()
        result = workflow.run()

        print(result.outputs.result)

    ```
3. Run it!

    ```bash
    python my_workflow.py

Note: To use most out-of-box Nodes, and to push/pull to/from the Vellum UI, you'll need a Vellum account and API key.
You can [sign up for free here](https://app.vellum.ai/signup?f=wsdk&utm_source=github&utm_medium=repo_quickstart&utm_campaign=sdk).


## Documentation
Complete documentation for the Vellum Workflows SDK can be found at https://docs.vellum.ai/developers/workflows-sdk.


## Stability

This SDK is currently in <Availability type="beta" /> and is subject to change. If you'd like to participate in
our beta program, please [contact us](https://docs.vellum.ai/home/getting-started/support).
