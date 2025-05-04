# Custom Prompt Node

This Workflow is an example of implementing your _own_ Prompt node that avoids making the round trip to Vellum by invoking the LLM directly. The node, `LocalBedrockNode`, assumes that you have your AWS credentials stored locally in a `.env` file in order to run locally:

```bash
VELLUM_API_KEY=*************************
AWS_ACCESS_KEY_ID=**********************
AWS_SECRET_ACCESS_KEY=******************
```

It also depends on a dependency called `boto3`, which acts as a client to the AWS API. To use it in Vellum, you will need to build the Docker image locally:

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
vellum workflows push custom_prompt_node
```
