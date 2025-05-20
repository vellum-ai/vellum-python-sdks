# Reference
<details><summary><code>client.<a href="src/vellum/client.py">execute_api</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.execute_api(
    url="url",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**url:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**method:** `typing.Optional[MethodEnum]` 
    
</dd>
</dl>

<dl>
<dd>

**body:** `typing.Optional[ExecuteApiRequestBody]` 
    
</dd>
</dl>

<dl>
<dd>

**headers:** `typing.Optional[typing.Dict[str, ExecuteApiRequestHeadersValue]]` 
    
</dd>
</dl>

<dl>
<dd>

**bearer_token:** `typing.Optional[ExecuteApiRequestBearerToken]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/vellum/client.py">execute_code</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import CodeExecutionPackage, StringInput, Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.execute_code(
    code="code",
    runtime="PYTHON_3_11_6",
    input_values=[
        StringInput(
            name="name",
            value="value",
        )
    ],
    packages=[
        CodeExecutionPackage(
            version="version",
            name="name",
        )
    ],
    output_type="STRING",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**code:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**runtime:** `CodeExecutionRuntime` 
    
</dd>
</dl>

<dl>
<dd>

**input_values:** `typing.Sequence[CodeExecutorInput]` 
    
</dd>
</dl>

<dl>
<dd>

**packages:** `typing.Sequence[CodeExecutionPackage]` 
    
</dd>
</dl>

<dl>
<dd>

**output_type:** `VellumVariableType` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/vellum/client.py">execute_prompt</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Executes a deployed Prompt and returns the result.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import StringInputRequest, Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.execute_prompt(
    inputs=[
        StringInputRequest(
            name="name",
            value="value",
        )
    ],
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**inputs:** `typing.Sequence[PromptDeploymentInputRequest]` — A list consisting of the Prompt Deployment's input variables and their values.
    
</dd>
</dl>

<dl>
<dd>

**prompt_deployment_id:** `typing.Optional[str]` — The ID of the Prompt Deployment. Must provide either this or prompt_deployment_name.
    
</dd>
</dl>

<dl>
<dd>

**prompt_deployment_name:** `typing.Optional[str]` — The unique name of the Prompt Deployment. Must provide either this or prompt_deployment_id.
    
</dd>
</dl>

<dl>
<dd>

**release_tag:** `typing.Optional[str]` — Optionally specify a release tag if you want to pin to a specific release of the Prompt Deployment
    
</dd>
</dl>

<dl>
<dd>

**external_id:** `typing.Optional[str]` — Optionally include a unique identifier for tracking purposes. Must be unique within a given Workspace.
    
</dd>
</dl>

<dl>
<dd>

**expand_meta:** `typing.Optional[PromptDeploymentExpandMetaRequest]` — An optionally specified configuration used to opt in to including additional metadata about this prompt execution in the API response. Corresponding values will be returned under the `meta` key of the API response.
    
</dd>
</dl>

<dl>
<dd>

**raw_overrides:** `typing.Optional[RawPromptExecutionOverridesRequest]` — Overrides for the raw API request sent to the model host. Combined with `expand_raw`, it can be used to access new features from models.
    
</dd>
</dl>

<dl>
<dd>

**expand_raw:** `typing.Optional[typing.Sequence[str]]` — A list of keys whose values you'd like to directly return from the JSON response of the model provider. Useful if you need lower-level info returned by model providers that Vellum would otherwise omit. Corresponding key/value pairs will be returned under the `raw` key of the API response.
    
</dd>
</dl>

<dl>
<dd>

**metadata:** `typing.Optional[typing.Dict[str, typing.Optional[typing.Any]]]` — Arbitrary JSON metadata associated with this request. Can be used to capture additional monitoring data such as user id, session id, etc. for future analysis.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/vellum/client.py">execute_prompt_stream</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Executes a deployed Prompt and streams back the results.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import StringInputRequest, Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
response = client.execute_prompt_stream(
    inputs=[
        StringInputRequest(
            name="name",
            value="value",
        )
    ],
)
for chunk in response:
    yield chunk

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**inputs:** `typing.Sequence[PromptDeploymentInputRequest]` — A list consisting of the Prompt Deployment's input variables and their values.
    
</dd>
</dl>

<dl>
<dd>

**prompt_deployment_id:** `typing.Optional[str]` — The ID of the Prompt Deployment. Must provide either this or prompt_deployment_name.
    
</dd>
</dl>

<dl>
<dd>

**prompt_deployment_name:** `typing.Optional[str]` — The unique name of the Prompt Deployment. Must provide either this or prompt_deployment_id.
    
</dd>
</dl>

<dl>
<dd>

**release_tag:** `typing.Optional[str]` — Optionally specify a release tag if you want to pin to a specific release of the Prompt Deployment
    
</dd>
</dl>

<dl>
<dd>

**external_id:** `typing.Optional[str]` — Optionally include a unique identifier for tracking purposes. Must be unique within a given Workspace.
    
</dd>
</dl>

<dl>
<dd>

**expand_meta:** `typing.Optional[PromptDeploymentExpandMetaRequest]` — An optionally specified configuration used to opt in to including additional metadata about this prompt execution in the API response. Corresponding values will be returned under the `meta` key of the API response.
    
</dd>
</dl>

<dl>
<dd>

**raw_overrides:** `typing.Optional[RawPromptExecutionOverridesRequest]` — Overrides for the raw API request sent to the model host. Combined with `expand_raw`, it can be used to access new features from models.
    
</dd>
</dl>

<dl>
<dd>

**expand_raw:** `typing.Optional[typing.Sequence[str]]` — A list of keys whose values you'd like to directly return from the JSON response of the model provider. Useful if you need lower-level info returned by model providers that Vellum would otherwise omit. Corresponding key/value pairs will be returned under the `raw` key of the API response.
    
</dd>
</dl>

<dl>
<dd>

**metadata:** `typing.Optional[typing.Dict[str, typing.Optional[typing.Any]]]` — Arbitrary JSON metadata associated with this request. Can be used to capture additional monitoring data such as user id, session id, etc. for future analysis.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/vellum/client.py">execute_workflow</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Executes a deployed Workflow and returns its outputs.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum, WorkflowRequestStringInputRequest

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.execute_workflow(
    inputs=[
        WorkflowRequestStringInputRequest(
            name="name",
            value="value",
        )
    ],
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**inputs:** `typing.Sequence[WorkflowRequestInputRequest]` — The list of inputs defined in the Workflow's Deployment with their corresponding values.
    
</dd>
</dl>

<dl>
<dd>

**expand_meta:** `typing.Optional[WorkflowExpandMetaRequest]` — An optionally specified configuration used to opt in to including additional metadata about this workflow execution in the API response. Corresponding values will be returned under the `execution_meta` key within NODE events in the response stream.
    
</dd>
</dl>

<dl>
<dd>

**workflow_deployment_id:** `typing.Optional[str]` — The ID of the Workflow Deployment. Must provide either this or workflow_deployment_name.
    
</dd>
</dl>

<dl>
<dd>

**workflow_deployment_name:** `typing.Optional[str]` — The name of the Workflow Deployment. Must provide either this or workflow_deployment_id.
    
</dd>
</dl>

<dl>
<dd>

**release_tag:** `typing.Optional[str]` — Optionally specify a release tag if you want to pin to a specific release of the Workflow Deployment
    
</dd>
</dl>

<dl>
<dd>

**external_id:** `typing.Optional[str]` — Optionally include a unique identifier for tracking purposes. Must be unique within a given Workspace.
    
</dd>
</dl>

<dl>
<dd>

**metadata:** `typing.Optional[typing.Dict[str, typing.Optional[typing.Any]]]` — Arbitrary JSON metadata associated with this request. Can be used to capture additional monitoring data such as user id, session id, etc. for future analysis.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/vellum/client.py">execute_workflow_stream</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Executes a deployed Workflow and streams back its results.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum, WorkflowRequestStringInputRequest

client = Vellum(
    api_key="YOUR_API_KEY",
)
response = client.execute_workflow_stream(
    inputs=[
        WorkflowRequestStringInputRequest(
            name="name",
            value="value",
        )
    ],
)
for chunk in response:
    yield chunk

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**inputs:** `typing.Sequence[WorkflowRequestInputRequest]` — The list of inputs defined in the Workflow's Deployment with their corresponding values.
    
</dd>
</dl>

<dl>
<dd>

**expand_meta:** `typing.Optional[WorkflowExpandMetaRequest]` — An optionally specified configuration used to opt in to including additional metadata about this workflow execution in the API response. Corresponding values will be returned under the `execution_meta` key within NODE events in the response stream.
    
</dd>
</dl>

<dl>
<dd>

**workflow_deployment_id:** `typing.Optional[str]` — The ID of the Workflow Deployment. Must provide either this or workflow_deployment_name.
    
</dd>
</dl>

<dl>
<dd>

**workflow_deployment_name:** `typing.Optional[str]` — The name of the Workflow Deployment. Must provide either this or workflow_deployment_id.
    
</dd>
</dl>

<dl>
<dd>

**release_tag:** `typing.Optional[str]` — Optionally specify a release tag if you want to pin to a specific release of the Workflow Deployment
    
</dd>
</dl>

<dl>
<dd>

**external_id:** `typing.Optional[str]` — Optionally include a unique identifier for tracking purposes. Must be unique within a given Workspace.
    
</dd>
</dl>

<dl>
<dd>

**event_types:** `typing.Optional[typing.Sequence[WorkflowExecutionEventType]]` — Optionally specify which events you want to receive. Defaults to only WORKFLOW events. Note that the schema of non-WORKFLOW events is unstable and should be used with caution.
    
</dd>
</dl>

<dl>
<dd>

**metadata:** `typing.Optional[typing.Dict[str, typing.Optional[typing.Any]]]` — Arbitrary JSON metadata associated with this request. Can be used to capture additional monitoring data such as user id, session id, etc. for future analysis.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/vellum/client.py">generate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Generate a completion using a previously defined deployment.

Important: This endpoint is DEPRECATED and has been superseded by
[execute-prompt](/api-reference/api-reference/execute-prompt).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import GenerateRequest, Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.generate(
    requests=[
        GenerateRequest(
            input_values={"key": "value"},
        )
    ],
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**requests:** `typing.Sequence[GenerateRequest]` — The generation request to make. Bulk requests are no longer supported, this field must be an array of length 1.
    
</dd>
</dl>

<dl>
<dd>

**deployment_id:** `typing.Optional[str]` — The ID of the deployment. Must provide either this or deployment_name.
    
</dd>
</dl>

<dl>
<dd>

**deployment_name:** `typing.Optional[str]` — The name of the deployment. Must provide either this or deployment_id.
    
</dd>
</dl>

<dl>
<dd>

**options:** `typing.Optional[GenerateOptionsRequest]` — Additional configuration that can be used to control what's included in the response.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/vellum/client.py">generate_stream</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Generate a stream of completions using a previously defined deployment.

Important: This endpoint is DEPRECATED and has been superseded by
[execute-prompt-stream](/api-reference/api-reference/execute-prompt-stream).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import GenerateRequest, Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
response = client.generate_stream(
    requests=[
        GenerateRequest(
            input_values={"key": "value"},
        )
    ],
)
for chunk in response:
    yield chunk

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**requests:** `typing.Sequence[GenerateRequest]` — The generation request to make. Bulk requests are no longer supported, this field must be an array of length 1.
    
</dd>
</dl>

<dl>
<dd>

**deployment_id:** `typing.Optional[str]` — The ID of the deployment. Must provide either this or deployment_name.
    
</dd>
</dl>

<dl>
<dd>

**deployment_name:** `typing.Optional[str]` — The name of the deployment. Must provide either this or deployment_id.
    
</dd>
</dl>

<dl>
<dd>

**options:** `typing.Optional[GenerateOptionsRequest]` — Additional configuration that can be used to control what's included in the response.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/vellum/client.py">search</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Perform a search against a document index.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.search(
    query="query",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**query:** `str` — The query to search for.
    
</dd>
</dl>

<dl>
<dd>

**index_id:** `typing.Optional[str]` — The ID of the index to search against. Must provide either this, index_name or document_index.
    
</dd>
</dl>

<dl>
<dd>

**index_name:** `typing.Optional[str]` — The name of the index to search against. Must provide either this, index_id or document_index.
    
</dd>
</dl>

<dl>
<dd>

**options:** `typing.Optional[SearchRequestOptionsRequest]` — Configuration options for the search.
    
</dd>
</dl>

<dl>
<dd>

**document_index:** `typing.Optional[str]` — Either the index name or index ID to search against. Must provide either this, index_id or index_name.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/vellum/client.py">submit_completion_actuals</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Used to submit feedback regarding the quality of previously generated completions.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import SubmitCompletionActualRequest, Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.submit_completion_actuals(
    actuals=[SubmitCompletionActualRequest()],
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**actuals:** `typing.Sequence[SubmitCompletionActualRequest]` — Feedback regarding the quality of previously generated completions
    
</dd>
</dl>

<dl>
<dd>

**deployment_id:** `typing.Optional[str]` — The ID of the deployment. Must provide either this or deployment_name.
    
</dd>
</dl>

<dl>
<dd>

**deployment_name:** `typing.Optional[str]` — The name of the deployment. Must provide either this or deployment_id.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/vellum/client.py">submit_workflow_execution_actuals</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

    Used to submit feedback regarding the quality of previous workflow execution and its outputs.

    **Note:** Uses a base url of `https://predict.vellum.ai`.    
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum, WorkflowExecutionActualStringRequest

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.submit_workflow_execution_actuals(
    actuals=[WorkflowExecutionActualStringRequest()],
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**actuals:** `typing.Sequence[SubmitWorkflowExecutionActualRequest]` — Feedback regarding the quality of an output on a previously executed workflow.
    
</dd>
</dl>

<dl>
<dd>

**execution_id:** `typing.Optional[str]` — The Vellum-generated ID of a previously executed workflow. Must provide either this or external_id.
    
</dd>
</dl>

<dl>
<dd>

**external_id:** `typing.Optional[str]` — The external ID that was originally provided by when executing the workflow, if applicable, that you'd now like to submit actuals for. Must provide either this or execution_id.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## AdHoc
<details><summary><code>client.ad_hoc.<a href="src/vellum/resources/ad_hoc/client.py">adhoc_execute_prompt</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import (
    JinjaPromptBlock,
    PromptParameters,
    PromptRequestStringInput,
    Vellum,
    VellumVariable,
)

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.ad_hoc.adhoc_execute_prompt(
    ml_model="ml_model",
    input_values=[
        PromptRequestStringInput(
            key="key",
            value="value",
        )
    ],
    input_variables=[
        VellumVariable(
            id="id",
            key="key",
            type="STRING",
        )
    ],
    parameters=PromptParameters(),
    blocks=[
        JinjaPromptBlock(
            template="template",
        )
    ],
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**ml_model:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**input_values:** `typing.Sequence[PromptRequestInput]` 
    
</dd>
</dl>

<dl>
<dd>

**input_variables:** `typing.Sequence[VellumVariable]` 
    
</dd>
</dl>

<dl>
<dd>

**parameters:** `PromptParameters` 
    
</dd>
</dl>

<dl>
<dd>

**blocks:** `typing.Sequence[PromptBlock]` 
    
</dd>
</dl>

<dl>
<dd>

**settings:** `typing.Optional[PromptSettings]` 
    
</dd>
</dl>

<dl>
<dd>

**functions:** `typing.Optional[typing.Sequence[FunctionDefinition]]` 
    
</dd>
</dl>

<dl>
<dd>

**expand_meta:** `typing.Optional[AdHocExpandMeta]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.ad_hoc.<a href="src/vellum/resources/ad_hoc/client.py">adhoc_execute_prompt_stream</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import (
    JinjaPromptBlock,
    PromptParameters,
    PromptRequestStringInput,
    Vellum,
    VellumVariable,
)

client = Vellum(
    api_key="YOUR_API_KEY",
)
response = client.ad_hoc.adhoc_execute_prompt_stream(
    ml_model="ml_model",
    input_values=[
        PromptRequestStringInput(
            key="key",
            value="value",
        )
    ],
    input_variables=[
        VellumVariable(
            id="id",
            key="key",
            type="STRING",
        )
    ],
    parameters=PromptParameters(),
    blocks=[
        JinjaPromptBlock(
            template="template",
        )
    ],
)
for chunk in response:
    yield chunk

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**ml_model:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**input_values:** `typing.Sequence[PromptRequestInput]` 
    
</dd>
</dl>

<dl>
<dd>

**input_variables:** `typing.Sequence[VellumVariable]` 
    
</dd>
</dl>

<dl>
<dd>

**parameters:** `PromptParameters` 
    
</dd>
</dl>

<dl>
<dd>

**blocks:** `typing.Sequence[PromptBlock]` 
    
</dd>
</dl>

<dl>
<dd>

**settings:** `typing.Optional[PromptSettings]` 
    
</dd>
</dl>

<dl>
<dd>

**functions:** `typing.Optional[typing.Sequence[FunctionDefinition]]` 
    
</dd>
</dl>

<dl>
<dd>

**expand_meta:** `typing.Optional[AdHocExpandMeta]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## ContainerImages
<details><summary><code>client.container_images.<a href="src/vellum/resources/container_images/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a list of container images for the organization.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.container_images.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Number of results to return per page.
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]` — The initial index from which to return the results.
    
</dd>
</dl>

<dl>
<dd>

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.container_images.<a href="src/vellum/resources/container_images/client.py">retrieve</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a Container Image by its ID or name.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.container_images.retrieve(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — Either the Container Image's ID or its unique name
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.container_images.<a href="src/vellum/resources/container_images/client.py">docker_service_token</a>()</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.container_images.docker_service_token()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.container_images.<a href="src/vellum/resources/container_images/client.py">push_container_image</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.container_images.push_container_image(
    name="name",
    sha="sha",
    tags=["tags"],
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**sha:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**tags:** `typing.Sequence[str]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Deployments
<details><summary><code>client.deployments.<a href="src/vellum/resources/deployments/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Used to list all Prompt Deployments.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.deployments.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Number of results to return per page.
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]` — The initial index from which to return the results.
    
</dd>
</dl>

<dl>
<dd>

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[DeploymentsListRequestStatus]` — status
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.deployments.<a href="src/vellum/resources/deployments/client.py">retrieve</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Used to retrieve a Prompt Deployment given its ID or name.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.deployments.retrieve(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — Either the Prompt Deployment's ID or its unique name
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.deployments.<a href="src/vellum/resources/deployments/client.py">deployment_history_item_retrieve</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

DEPRECATED: This endpoint is deprecated and will be removed in a future release. Please use the
`retrieve_prompt_deployment_release` xendpoint instead.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.deployments.deployment_history_item_retrieve(
    history_id_or_release_tag="history_id_or_release_tag",
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**history_id_or_release_tag:** `str` — Either the UUID of Deployment History Item you'd like to retrieve, or the name of a Release Tag that's pointing to the Deployment History Item you'd like to retrieve.
    
</dd>
</dl>

<dl>
<dd>

**id:** `str` — Either the Prompt Deployment's ID or its unique name
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.deployments.<a href="src/vellum/resources/deployments/client.py">list_deployment_release_tags</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List Release Tags associated with the specified Prompt Deployment
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.deployments.list_deployment_release_tags(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — Either the Prompt Deployment's ID or its unique name
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Number of results to return per page.
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]` — The initial index from which to return the results.
    
</dd>
</dl>

<dl>
<dd>

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
</dd>
</dl>

<dl>
<dd>

**source:** `typing.Optional[ListDeploymentReleaseTagsRequestSource]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.deployments.<a href="src/vellum/resources/deployments/client.py">retrieve_deployment_release_tag</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a Deployment Release Tag by tag name, associated with a specified Deployment.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.deployments.retrieve_deployment_release_tag(
    id="id",
    name="name",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — Either the Prompt Deployment's ID or its unique name
    
</dd>
</dl>

<dl>
<dd>

**name:** `str` — The name of the Release Tag associated with this Deployment that you'd like to retrieve.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.deployments.<a href="src/vellum/resources/deployments/client.py">update_deployment_release_tag</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Updates an existing Release Tag associated with the specified Prompt Deployment.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.deployments.update_deployment_release_tag(
    id="id",
    name="name",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — Either the Prompt Deployment's ID or its unique name
    
</dd>
</dl>

<dl>
<dd>

**name:** `str` — The name of the Release Tag associated with this Deployment that you'd like to update.
    
</dd>
</dl>

<dl>
<dd>

**history_item_id:** `typing.Optional[str]` — The ID of the Release to tag
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.deployments.<a href="src/vellum/resources/deployments/client.py">retrieve_prompt_deployment_release</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a specific Prompt Deployment Release by either its UUID or the name of a Release Tag that points to it.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.deployments.retrieve_prompt_deployment_release(
    id="id",
    release_id_or_release_tag="release_id_or_release_tag",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — Either the Prompt Deployment's ID or its unique name
    
</dd>
</dl>

<dl>
<dd>

**release_id_or_release_tag:** `str` — Either the UUID of Prompt Deployment Release you'd like to retrieve, or the name of a Release Tag that's pointing to the Prompt Deployment Release you'd like to retrieve.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.deployments.<a href="src/vellum/resources/deployments/client.py">retrieve_provider_payload</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Given a set of input variable values, compile the exact payload that Vellum would send to the configured model provider
for execution if the execute-prompt endpoint had been invoked. Note that this endpoint does not actually execute the
prompt or make an API call to the model provider.

This endpoint is useful if you don't want to proxy LLM provider requests through Vellum and prefer to send them directly
to the provider yourself. Note that no guarantees are made on the format of this API's response schema, other than
that it will be a valid payload for the configured model provider. It's not recommended that you try to parse or
derive meaning from the response body and instead, should simply pass it directly to the model provider as is.

We encourage you to seek advise from Vellum Support before integrating with this API for production use.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import StringInputRequest, Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.deployments.retrieve_provider_payload(
    inputs=[
        StringInputRequest(
            name="name",
            value="value",
        )
    ],
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**inputs:** `typing.Sequence[PromptDeploymentInputRequest]` — The list of inputs defined in the Prompt's deployment with their corresponding values.
    
</dd>
</dl>

<dl>
<dd>

**deployment_id:** `typing.Optional[str]` — The ID of the deployment. Must provide either this or deployment_name.
    
</dd>
</dl>

<dl>
<dd>

**deployment_name:** `typing.Optional[str]` — The name of the deployment. Must provide either this or deployment_id.
    
</dd>
</dl>

<dl>
<dd>

**release_tag:** `typing.Optional[str]` — Optionally specify a release tag if you want to pin to a specific release of the Workflow Deployment
    
</dd>
</dl>

<dl>
<dd>

**expand_meta:** `typing.Optional[CompilePromptDeploymentExpandMetaRequest]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## DocumentIndexes
<details><summary><code>client.document_indexes.<a href="src/vellum/resources/document_indexes/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Used to retrieve a list of Document Indexes.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.document_indexes.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Number of results to return per page.
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]` — The initial index from which to return the results.
    
</dd>
</dl>

<dl>
<dd>

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
</dd>
</dl>

<dl>
<dd>

**search:** `typing.Optional[str]` — Search for document indices by name or label
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[DocumentIndexesListRequestStatus]` 

Filter down to only document indices that have a status matching the status specified

* `ACTIVE` - Active
* `ARCHIVED` - Archived
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.document_indexes.<a href="src/vellum/resources/document_indexes/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a new document index.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import (
    DocumentIndexIndexingConfigRequest,
    OpenAiVectorizerConfigRequest,
    OpenAiVectorizerTextEmbeddingAda002Request,
    SentenceChunkerConfigRequest,
    SentenceChunkingRequest,
    Vellum,
)

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.document_indexes.create(
    label="My Document Index",
    name="my-document-index",
    indexing_config=DocumentIndexIndexingConfigRequest(
        vectorizer=OpenAiVectorizerTextEmbeddingAda002Request(
            config=OpenAiVectorizerConfigRequest(
                add_openai_api_key=True,
            ),
        ),
        chunking=SentenceChunkingRequest(
            chunker_config=SentenceChunkerConfigRequest(
                character_limit=1000,
                min_overlap_ratio=0.5,
            ),
        ),
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**label:** `str` — A human-readable label for the document index
    
</dd>
</dl>

<dl>
<dd>

**name:** `str` — A name that uniquely identifies this index within its workspace
    
</dd>
</dl>

<dl>
<dd>

**indexing_config:** `DocumentIndexIndexingConfigRequest` 
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[EntityStatus]` 

The current status of the document index

* `ACTIVE` - Active
* `ARCHIVED` - Archived
    
</dd>
</dl>

<dl>
<dd>

**copy_documents_from_index_id:** `typing.Optional[str]` — Optionally specify the id of a document index from which you'd like to copy and re-index its documents into this newly created index
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.document_indexes.<a href="src/vellum/resources/document_indexes/client.py">retrieve</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Used to retrieve a Document Index given its ID or name.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.document_indexes.retrieve(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — Either the Document Index's ID or its unique name
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.document_indexes.<a href="src/vellum/resources/document_indexes/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Used to fully update a Document Index given its ID or name.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.document_indexes.update(
    id="id",
    label="label",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — Either the Document Index's ID or its unique name
    
</dd>
</dl>

<dl>
<dd>

**label:** `str` — A human-readable label for the document index
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[EntityStatus]` 

The current status of the document index

* `ACTIVE` - Active
* `ARCHIVED` - Archived
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.document_indexes.<a href="src/vellum/resources/document_indexes/client.py">destroy</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Used to delete a Document Index given its ID or name.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.document_indexes.destroy(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — Either the Document Index's ID or its unique name
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.document_indexes.<a href="src/vellum/resources/document_indexes/client.py">partial_update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Used to partial update a Document Index given its ID or name.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.document_indexes.partial_update(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — Either the Document Index's ID or its unique name
    
</dd>
</dl>

<dl>
<dd>

**label:** `typing.Optional[str]` — A human-readable label for the document index
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[EntityStatus]` 

The current status of the document index

* `ACTIVE` - Active
* `ARCHIVED` - Archived
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.document_indexes.<a href="src/vellum/resources/document_indexes/client.py">add_document</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Adds a previously uploaded Document to the specified Document Index.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.document_indexes.add_document(
    document_id="document_id",
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**document_id:** `str` — Either the Vellum-generated ID or the originally supplied external_id that uniquely identifies the Document you'd like to add.
    
</dd>
</dl>

<dl>
<dd>

**id:** `str` — Either the Vellum-generated ID or the originally specified name that uniquely identifies the Document Index to which you'd like to add the Document.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.document_indexes.<a href="src/vellum/resources/document_indexes/client.py">remove_document</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Removes a Document from a Document Index without deleting the Document itself.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.document_indexes.remove_document(
    document_id="document_id",
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**document_id:** `str` — Either the Vellum-generated ID or the originally supplied external_id that uniquely identifies the Document you'd like to remove.
    
</dd>
</dl>

<dl>
<dd>

**id:** `str` — Either the Vellum-generated ID or the originally specified name that uniquely identifies the Document Index from which you'd like to remove a Document.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Documents
<details><summary><code>client.documents.<a href="src/vellum/resources/documents/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Used to list documents. Optionally filter on supported fields.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.documents.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**document_index_id:** `typing.Optional[str]` — Filter down to only those documents that are included in the specified index. You may provide either the Vellum-generated ID or the unique name of the index specified upon initial creation.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Number of results to return per page.
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]` — The initial index from which to return the results.
    
</dd>
</dl>

<dl>
<dd>

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
</dd>
</dl>

<dl>
<dd>

**search:** `typing.Optional[str]` — A search term.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.documents.<a href="src/vellum/resources/documents/client.py">retrieve</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a Document, keying off of either its Vellum-generated ID or its external ID.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.documents.retrieve(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.documents.<a href="src/vellum/resources/documents/client.py">destroy</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a Document, keying off of either its Vellum-generated ID or its external ID.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.documents.destroy(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.documents.<a href="src/vellum/resources/documents/client.py">partial_update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a Document, keying off of either its Vellum-generated ID or its external ID. Particularly useful for updating its metadata.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.documents.partial_update(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**label:** `typing.Optional[str]` — A human-readable label for the document. Defaults to the originally uploaded file's file name.
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[DocumentStatus]` 

The current status of the document

* `ACTIVE` - Active
    
</dd>
</dl>

<dl>
<dd>

**metadata:** `typing.Optional[typing.Dict[str, typing.Optional[typing.Any]]]` — A JSON object containing any metadata associated with the document that you'd like to filter upon later.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.documents.<a href="src/vellum/resources/documents/client.py">upload</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Upload a document to be indexed and used for search.

**Note:** Uses a base url of `https://documents.vellum.ai`.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.documents.upload(
    label="label",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**label:** `str` — A human-friendly name for this document. Typically the filename.
    
</dd>
</dl>

<dl>
<dd>

**contents:** `from __future__ import annotations

core.File` — See core.File for more documentation
    
</dd>
</dl>

<dl>
<dd>

**add_to_index_names:** `typing.Optional[typing.List[str]]` — Optionally include the names of all indexes that you'd like this document to be included in
    
</dd>
</dl>

<dl>
<dd>

**external_id:** `typing.Optional[str]` — Optionally include an external ID for this document. This is useful if you want to re-upload the same document later when its contents change and would like it to be re-indexed.
    
</dd>
</dl>

<dl>
<dd>

**keywords:** `typing.Optional[typing.List[str]]` — Optionally include a list of keywords that'll be associated with this document. Used when performing keyword searches.
    
</dd>
</dl>

<dl>
<dd>

**metadata:** `typing.Optional[str]` — A stringified JSON object containing any metadata associated with the document that you'd like to filter upon later.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## FolderEntities
<details><summary><code>client.folder_entities.<a href="src/vellum/resources/folder_entities/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List all folder entities within a specified folder.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import Vellum

client = Vellum(
    api_key="YOUR_API_KEY",
)
client.folder_entities.list(
    parent_folder_id="parent_folder_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**parent_folder_id:** `str` 

Filter down to only those entities whose parent folder has the specified ID.

To filter by an entity's parent folder, provide the ID of the parent folder. To filter by the root directory, provide
a string representing the entity type of the root directory. Supported root directories include:
- PROMPT_SANDBOX
- WORKFLOW_SANDBOX
- DOCUMENT_INDEX
- TEST_SUITE
    
</dd>
</dl>

<dl>
<dd>

**entity_status:** `typing.Optional[FolderEntitiesListRequestEntityStatus]` 

Filter down to only those objects whose entities have a status matching the status specified.

* `ACTIVE` - Active
* `ARCHIVED` - Archived
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Number of results to return per page.
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]` — The initial index from which to return the results.
    
</dd>
</dl>

<dl>
<dd>

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.folder_entities.<a href="src/vellum/resources/folder_entities/client.py">add_entity_to_folder</a>(...)</code></summary>
