# Custom Base Node

_NOTE: This Workflow is still under development and is not yet ready for reuse_

This Workflow is an example of having multiple nodes extending from a Custom Node that the user defines, called `MockNetworkingClient`. This node simulates a client that makes a network call, whether that is HTTP, GraphQL, etc.

The node also imports logic from a module outside of the node, motivating the need for a [Custom Docker Image](https://docs.vellum.ai/developers/workflows-sdk/custom-container-images). The definition for this Docker image is found at `./utils/Dockerfile`. To rebuild locally, run:

```bash
docker buildx build -f utils/Dockerfile --platform=linux/amd64 -t sdk-examples-utils:1.0.0 .
```

Then, you could push the image to Vellum,

```bash
vellum images push sdk-examples-utils:1.0.0
```

Next, associate the newly created image with your workflow by adding the following to your `pyproject.toml`:

```toml
[[tool.vellum.workflows]]
module = "custom_prompt_node"
container_image_name = "sdk-examples-utils"
container_image_tag = "1.0.0"
```

You can then push the Workflow itself,

```bash
vellum workflows push custom_base_node
```
