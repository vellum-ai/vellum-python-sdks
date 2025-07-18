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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.execute_api(
    url="x",
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.execute_code(
    code="x",
    runtime="PYTHON_3_11_6",
    input_values=[
        StringInput(
            name="x",
            value="value",
        ),
        StringInput(
            name="x",
            value="value",
        ),
    ],
    packages=[
        CodeExecutionPackage(
            version="version",
            name="name",
        ),
        CodeExecutionPackage(
            version="version",
            name="name",
        ),
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.execute_prompt(
    inputs=[
        StringInputRequest(
            name="x",
            value="value",
        ),
        StringInputRequest(
            name="x",
            value="value",
        ),
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
response = client.execute_prompt_stream(
    inputs=[
        StringInputRequest(
            name="x",
            value="value",
        ),
        StringInputRequest(
            name="x",
            value="value",
        ),
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.execute_workflow(
    inputs=[
        WorkflowRequestStringInputRequest(
            name="x",
            value="value",
        ),
        WorkflowRequestStringInputRequest(
            name="x",
            value="value",
        ),
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
response = client.execute_workflow_stream(
    inputs=[
        WorkflowRequestStringInputRequest(
            name="x",
            value="value",
        ),
        WorkflowRequestStringInputRequest(
            name="x",
            value="value",
        ),
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.generate(
    requests=[
        GenerateRequest(
            input_values={"input_values": {"key": "value"}},
        ),
        GenerateRequest(
            input_values={"input_values": {"key": "value"}},
        ),
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
response = client.generate_stream(
    requests=[
        GenerateRequest(
            input_values={"input_values": {"key": "value"}},
        ),
        GenerateRequest(
            input_values={"input_values": {"key": "value"}},
        ),
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.search(
    query="x",
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.submit_completion_actuals(
    actuals=[SubmitCompletionActualRequest(), SubmitCompletionActualRequest()],
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.submit_workflow_execution_actuals(
    actuals=[
        WorkflowExecutionActualStringRequest(),
        WorkflowExecutionActualStringRequest(),
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.ad_hoc.adhoc_execute_prompt(
    ml_model="x",
    input_values=[
        PromptRequestStringInput(
            key="x",
            value="value",
        ),
        PromptRequestStringInput(
            key="x",
            value="value",
        ),
    ],
    input_variables=[
        VellumVariable(
            id="x",
            key="key",
            type="STRING",
        ),
        VellumVariable(
            id="x",
            key="key",
            type="STRING",
        ),
    ],
    parameters=PromptParameters(),
    blocks=[
        JinjaPromptBlock(
            template="template",
        ),
        JinjaPromptBlock(
            template="template",
        ),
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
response = client.ad_hoc.adhoc_execute_prompt_stream(
    ml_model="x",
    input_values=[
        PromptRequestStringInput(
            key="x",
            value="value",
        ),
        PromptRequestStringInput(
            key="x",
            value="value",
        ),
    ],
    input_variables=[
        VellumVariable(
            id="x",
            key="key",
            type="STRING",
        ),
        VellumVariable(
            id="x",
            key="key",
            type="STRING",
        ),
    ],
    parameters=PromptParameters(),
    blocks=[
        JinjaPromptBlock(
            template="template",
        ),
        JinjaPromptBlock(
            template="template",
        ),
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
    api_version="YOUR_API_VERSION",
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
    api_version="YOUR_API_VERSION",
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
    api_version="YOUR_API_VERSION",
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.container_images.push_container_image(
    name="x",
    sha="x",
    tags=["tags", "tags"],
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
    api_version="YOUR_API_VERSION",
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
    api_version="YOUR_API_VERSION",
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
    api_version="YOUR_API_VERSION",
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
    api_version="YOUR_API_VERSION",
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
    api_version="YOUR_API_VERSION",
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
    api_version="YOUR_API_VERSION",
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
    api_version="YOUR_API_VERSION",
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.deployments.retrieve_provider_payload(
    inputs=[
        StringInputRequest(
            name="x",
            value="value",
        ),
        StringInputRequest(
            name="x",
            value="value",
        ),
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
    api_version="YOUR_API_VERSION",
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
    OpenAiVectorizerTextEmbedding3SmallRequest,
    Vellum,
)

client = Vellum(
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.document_indexes.create(
    label="x",
    name="x",
    indexing_config=DocumentIndexIndexingConfigRequest(
        vectorizer=OpenAiVectorizerTextEmbedding3SmallRequest(
            config=OpenAiVectorizerConfigRequest(),
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
    api_version="YOUR_API_VERSION",
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.document_indexes.update(
    id="id",
    label="x",
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
    api_version="YOUR_API_VERSION",
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
    api_version="YOUR_API_VERSION",
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
    api_version="YOUR_API_VERSION",
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
    api_version="YOUR_API_VERSION",
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
    api_version="YOUR_API_VERSION",
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
    api_version="YOUR_API_VERSION",
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
    api_version="YOUR_API_VERSION",
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
    api_version="YOUR_API_VERSION",
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

**keywords:** `typing.Optional[typing.Sequence[str]]` — A list of keywords that'll be associated with the document. Used as part of keyword search.
    
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
    api_version="YOUR_API_VERSION",
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
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Add an entity to a specific folder or root directory.

Adding an entity to a folder will remove it from any other folders it might have been a member of.
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.folder_entities.add_entity_to_folder(
    folder_id="folder_id",
    entity_id="entity_id",
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

**folder_id:** `str` 

The ID of the folder to which the entity should be added. This can be a UUID of a folder, or the name of a root
directory. Supported root directories include:
- PROMPT_SANDBOX
- WORKFLOW_SANDBOX
- DOCUMENT_INDEX
- TEST_SUITE
    
</dd>
</dl>

<dl>
<dd>

**entity_id:** `str` — The ID of the entity you would like to move.
    
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

## MetricDefinitions
<details><summary><code>client.metric_definitions.<a href="src/vellum/resources/metric_definitions/client.py">execute_metric_definition</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from vellum import StringInput, Vellum

client = Vellum(
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.metric_definitions.execute_metric_definition(
    id="id",
    inputs=[
        StringInput(
            name="x",
            value="value",
        ),
        StringInput(
            name="x",
            value="value",
        ),
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

**id:** `str` — Either the Metric Definition's ID or its unique name
    
</dd>
</dl>

<dl>
<dd>

**inputs:** `typing.Sequence[MetricDefinitionInput]` 
    
</dd>
</dl>

<dl>
<dd>

**release_tag:** `typing.Optional[str]` 
    
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

<details><summary><code>client.metric_definitions.<a href="src/vellum/resources/metric_definitions/client.py">metric_definition_history_item_retrieve</a>(...)</code></summary>
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.metric_definitions.metric_definition_history_item_retrieve(
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

**history_id_or_release_tag:** `str` — Either the UUID of Metric Definition History Item you'd like to retrieve, or the name of a Release Tag that's pointing to the Metric Definition History Item you'd like to retrieve.
    
</dd>
</dl>

<dl>
<dd>

**id:** `str` — A UUID string identifying this metric definition.
    
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

## MlModels
<details><summary><code>client.ml_models.<a href="src/vellum/resources/ml_models/client.py">retrieve</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve details about an ML Model
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.ml_models.retrieve(
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

**id:** `str` — Either the ML Model's ID, its unique name, or its ID in the workspace.
    
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

## Organizations
<details><summary><code>client.organizations.<a href="src/vellum/resources/organizations/client.py">organization_identity</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieves information about the active Organization
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.organizations.organization_identity()

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

## Prompts
<details><summary><code>client.prompts.<a href="src/vellum/resources/prompts/client.py">pull</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Used to pull the definition of a Prompt from Vellum.
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.prompts.pull(
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

**id:** `str` — The ID of the Prompt to pull from. Prompt Sandbox IDs are currently supported.
    
</dd>
</dl>

<dl>
<dd>

**prompt_variant_id:** `typing.Optional[str]` — The ID of the Prompt Variant within a Prompt Sandbox to pull. Must be included if providing the ID of a Prompt Sandbox.
    
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

<details><summary><code>client.prompts.<a href="src/vellum/resources/prompts/client.py">push</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Used to push updates to a Prompt in Vellum.
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
    JinjaPromptBlock,
    PromptExecConfig,
    PromptParameters,
    Vellum,
    VellumVariable,
)

client = Vellum(
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.prompts.push(
    exec_config=PromptExecConfig(
        ml_model="ml_model",
        input_variables=[
            VellumVariable(
                id="x",
                key="key",
                type="STRING",
            ),
            VellumVariable(
                id="x",
                key="key",
                type="STRING",
            ),
        ],
        parameters=PromptParameters(),
        blocks=[
            JinjaPromptBlock(
                template="template",
            ),
            JinjaPromptBlock(
                template="template",
            ),
        ],
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

**exec_config:** `PromptExecConfig` 
    
</dd>
</dl>

<dl>
<dd>

**prompt_variant_id:** `typing.Optional[str]` — If specified, an existing Prompt Variant by the provided ID will be updated. Otherwise, a new Prompt Variant will be created and an ID generated.
    
</dd>
</dl>

<dl>
<dd>

**prompt_variant_label:** `typing.Optional[str]` — If provided, then the created/updated Prompt Variant will have this label.
    
</dd>
</dl>

<dl>
<dd>

**prompt_sandbox_id:** `typing.Optional[str]` 
    
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

## Sandboxes
<details><summary><code>client.sandboxes.<a href="src/vellum/resources/sandboxes/client.py">deploy_prompt</a>(...)</code></summary>
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.sandboxes.deploy_prompt(
    id="id",
    prompt_variant_id="prompt_variant_id",
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

**id:** `str` — A UUID string identifying this sandbox.
    
</dd>
</dl>

<dl>
<dd>

**prompt_variant_id:** `str` — An ID identifying the Prompt you'd like to deploy.
    
</dd>
</dl>

<dl>
<dd>

**prompt_deployment_id:** `typing.Optional[str]` — The Vellum-generated ID of the Prompt Deployment you'd like to update. Cannot specify both this and prompt_deployment_name. Leave null to create a new Prompt Deployment.
    
</dd>
</dl>

<dl>
<dd>

**prompt_deployment_name:** `typing.Optional[str]` — The unique name of the Prompt Deployment you'd like to either create or update. Cannot specify both this and prompt_deployment_id. If provided and matches an existing Prompt Deployment, that Prompt Deployment will be updated. Otherwise, a new Prompt Deployment will be created.
    
</dd>
</dl>

<dl>
<dd>

**label:** `typing.Optional[str]` — In the event that a new Prompt Deployment is created, this will be the label it's given.
    
</dd>
</dl>

<dl>
<dd>

**release_tags:** `typing.Optional[typing.Sequence[str]]` — Optionally provide the release tags that you'd like to be associated with the latest release of the created/updated Prompt Deployment.
    
</dd>
</dl>

<dl>
<dd>

**release_description:** `typing.Optional[str]` — Optionally provide a description that details what's new in this Release.
    
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

<details><summary><code>client.sandboxes.<a href="src/vellum/resources/sandboxes/client.py">upsert_sandbox_scenario</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Upserts a new scenario for a sandbox, keying off of the optionally provided scenario id.

If an id is provided and has a match, the scenario will be updated. If no id is provided or no match
is found, a new scenario will be appended to the end.

Note that a full replacement of the scenario is performed, so any fields not provided will be removed
or overwritten with default values.
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
from vellum import NamedScenarioInputStringVariableValueRequest, Vellum

client = Vellum(
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.sandboxes.upsert_sandbox_scenario(
    id="id",
    inputs=[
        NamedScenarioInputStringVariableValueRequest(
            name="x",
        ),
        NamedScenarioInputStringVariableValueRequest(
            name="x",
        ),
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

**id:** `str` — A UUID string identifying this sandbox.
    
</dd>
</dl>

<dl>
<dd>

**inputs:** `typing.Sequence[NamedScenarioInputRequest]` — The inputs for the scenario
    
</dd>
</dl>

<dl>
<dd>

**label:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**scenario_id:** `typing.Optional[str]` — The id of the scenario to update. If none is provided, an id will be generated and a new scenario will be appended.
    
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

<details><summary><code>client.sandboxes.<a href="src/vellum/resources/sandboxes/client.py">delete_sandbox_scenario</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes an existing scenario from a sandbox, keying off of the provided scenario id.
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.sandboxes.delete_sandbox_scenario(
    id="id",
    scenario_id="scenario_id",
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

**id:** `str` — A UUID string identifying this sandbox.
    
</dd>
</dl>

<dl>
<dd>

**scenario_id:** `str` — An id identifying the scenario that you'd like to delete
    
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

## TestSuiteRuns
<details><summary><code>client.test_suite_runs.<a href="src/vellum/resources/test_suite_runs/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Trigger a Test Suite and create a new Test Suite Run
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
    TestSuiteRunDeploymentReleaseTagExecConfigDataRequest,
    TestSuiteRunDeploymentReleaseTagExecConfigRequest,
    Vellum,
)

client = Vellum(
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.test_suite_runs.create(
    exec_config=TestSuiteRunDeploymentReleaseTagExecConfigRequest(
        data=TestSuiteRunDeploymentReleaseTagExecConfigDataRequest(
            deployment_id="deployment_id",
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

**exec_config:** `TestSuiteRunExecConfigRequest` — Configuration that defines how the Test Suite should be run
    
</dd>
</dl>

<dl>
<dd>

**test_suite_id:** `typing.Optional[str]` — The ID of the Test Suite to run. Must provide either this or test_suite_id.
    
</dd>
</dl>

<dl>
<dd>

**test_suite_name:** `typing.Optional[str]` — The name of the Test Suite to run. Must provide either this or test_suite_id.
    
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

<details><summary><code>client.test_suite_runs.<a href="src/vellum/resources/test_suite_runs/client.py">retrieve</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a specific Test Suite Run by ID
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.test_suite_runs.retrieve(
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

**id:** `str` — A UUID string identifying this test suite run.
    
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

<details><summary><code>client.test_suite_runs.<a href="src/vellum/resources/test_suite_runs/client.py">list_executions</a>(...)</code></summary>
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.test_suite_runs.list_executions(
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

**id:** `str` — A UUID string identifying this test suite run.
    
</dd>
</dl>

<dl>
<dd>

**expand:** `typing.Optional[typing.Union[str, typing.Sequence[str]]]` 

The response fields to expand for more information.
- 'results.metric_results.metric_label' expands the metric label for each metric result.
- 'results.metric_results.metric_definition' expands the metric definition for each metric result.
- 'results.metric_results.metric_definition.name' expands the metric definition name for each metric result.
    
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

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## TestSuites
<details><summary><code>client.test_suites.<a href="src/vellum/resources/test_suites/client.py">list_test_suite_test_cases</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List the Test Cases associated with a Test Suite
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.test_suites.list_test_suite_test_cases(
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

**id:** `str` — Either the Test Suites' ID or its unique name
    
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

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.test_suites.<a href="src/vellum/resources/test_suites/client.py">upsert_test_suite_test_case</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Upserts a new test case for a test suite, keying off of the optionally provided test case id.

If an id is provided and has a match, the test case will be updated. If no id is provided or no match
is found, a new test case will be appended to the end.

Note that a full replacement of the test case is performed, so any fields not provided will be removed
or overwritten with default values.
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
from vellum import NamedTestCaseStringVariableValueRequest, Vellum

client = Vellum(
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.test_suites.upsert_test_suite_test_case(
    id_="id",
    input_values=[
        NamedTestCaseStringVariableValueRequest(
            name="x",
        ),
        NamedTestCaseStringVariableValueRequest(
            name="x",
        ),
    ],
    evaluation_values=[
        NamedTestCaseStringVariableValueRequest(
            name="x",
        ),
        NamedTestCaseStringVariableValueRequest(
            name="x",
        ),
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

**id_:** `str` — Either the Test Suites' ID or its unique name
    
</dd>
</dl>

<dl>
<dd>

**input_values:** `typing.Sequence[NamedTestCaseVariableValueRequest]` — Values for each of the Test Case's input variables
    
</dd>
</dl>

<dl>
<dd>

**evaluation_values:** `typing.Sequence[NamedTestCaseVariableValueRequest]` — Values for each of the Test Case's evaluation variables
    
</dd>
</dl>

<dl>
<dd>

**id:** `typing.Optional[str]` — The Vellum-generated ID of an existing Test Case whose data you'd like to replace. If specified and no Test Case exists with this ID, a 404 will be returned.
    
</dd>
</dl>

<dl>
<dd>

**external_id:** `typing.Optional[str]` — An ID external to Vellum that uniquely identifies the Test Case that you'd like to create/update. If there's a match on a Test Case that was previously created with the same external_id, it will be updated. Otherwise, a new Test Case will be created with this value as its external_id. If no external_id is specified, then a new Test Case will always be created.
    
</dd>
</dl>

<dl>
<dd>

**label:** `typing.Optional[str]` — A human-readable label used to convey the intention of this Test Case
    
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

<details><summary><code>client.test_suites.<a href="src/vellum/resources/test_suites/client.py">test_suite_test_cases_bulk</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Created, replace, and delete Test Cases within the specified Test Suite in bulk
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
    CreateTestSuiteTestCaseRequest,
    NamedTestCaseStringVariableValueRequest,
    TestSuiteTestCaseCreateBulkOperationRequest,
    Vellum,
)

client = Vellum(
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
response = client.test_suites.test_suite_test_cases_bulk(
    id="id",
    request=[
        TestSuiteTestCaseCreateBulkOperationRequest(
            id="id",
            data=CreateTestSuiteTestCaseRequest(
                input_values=[
                    NamedTestCaseStringVariableValueRequest(
                        name="x",
                    ),
                    NamedTestCaseStringVariableValueRequest(
                        name="x",
                    ),
                ],
                evaluation_values=[
                    NamedTestCaseStringVariableValueRequest(
                        name="x",
                    ),
                    NamedTestCaseStringVariableValueRequest(
                        name="x",
                    ),
                ],
            ),
        ),
        TestSuiteTestCaseCreateBulkOperationRequest(
            id="id",
            data=CreateTestSuiteTestCaseRequest(
                input_values=[
                    NamedTestCaseStringVariableValueRequest(
                        name="x",
                    ),
                    NamedTestCaseStringVariableValueRequest(
                        name="x",
                    ),
                ],
                evaluation_values=[
                    NamedTestCaseStringVariableValueRequest(
                        name="x",
                    ),
                    NamedTestCaseStringVariableValueRequest(
                        name="x",
                    ),
                ],
            ),
        ),
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

**id:** `str` — Either the Test Suites' ID or its unique name
    
</dd>
</dl>

<dl>
<dd>

**request:** `typing.Sequence[TestSuiteTestCaseBulkOperationRequest]` 
    
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

<details><summary><code>client.test_suites.<a href="src/vellum/resources/test_suites/client.py">delete_test_suite_test_case</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes an existing test case for a test suite, keying off of the test case id.
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.test_suites.delete_test_suite_test_case(
    id="id",
    test_case_id="test_case_id",
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

**id:** `str` — Either the Test Suites' ID or its unique name
    
</dd>
</dl>

<dl>
<dd>

**test_case_id:** `str` — An id identifying the test case that you'd like to delete
    
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

## WorkflowDeployments
<details><summary><code>client.workflow_deployments.<a href="src/vellum/resources/workflow_deployments/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Used to list all Workflow Deployments.
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.workflow_deployments.list()

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

**status:** `typing.Optional[WorkflowDeploymentsListRequestStatus]` — status
    
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

<details><summary><code>client.workflow_deployments.<a href="src/vellum/resources/workflow_deployments/client.py">retrieve</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Used to retrieve a workflow deployment given its ID or name.
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.workflow_deployments.retrieve(
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

**id:** `str` — Either the Workflow Deployment's ID or its unique name
    
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

<details><summary><code>client.workflow_deployments.<a href="src/vellum/resources/workflow_deployments/client.py">list_workflow_deployment_event_executions</a>(...)</code></summary>
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.workflow_deployments.list_workflow_deployment_event_executions(
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

**filters:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Number of executions to return per page.
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]` — The initial index from which to return the executions.
    
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

<details><summary><code>client.workflow_deployments.<a href="src/vellum/resources/workflow_deployments/client.py">workflow_deployment_event_execution</a>(...)</code></summary>
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.workflow_deployments.workflow_deployment_event_execution(
    execution_id="execution_id",
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

**execution_id:** `str` 
    
</dd>
</dl>

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

<details><summary><code>client.workflow_deployments.<a href="src/vellum/resources/workflow_deployments/client.py">workflow_deployment_history_item_retrieve</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

DEPRECATED: This endpoint is deprecated and will be removed in a future release. Please use the
`retrieve_workflow_deployment_release` endpoint instead.
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.workflow_deployments.workflow_deployment_history_item_retrieve(
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

**history_id_or_release_tag:** `str` — Either the UUID of Workflow Deployment History Item you'd like to retrieve, or the name of a Release Tag that's pointing to the Workflow Deployment History Item you'd like to retrieve.
    
</dd>
</dl>

<dl>
<dd>

**id:** `str` — Either the Workflow Deployment's ID or its unique name
    
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

<details><summary><code>client.workflow_deployments.<a href="src/vellum/resources/workflow_deployments/client.py">list_workflow_release_tags</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List Release Tags associated with the specified Workflow Deployment
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.workflow_deployments.list_workflow_release_tags(
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

**id:** `str` — Either the Workflow Deployment's ID or its unique name
    
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

**source:** `typing.Optional[ListWorkflowReleaseTagsRequestSource]` 
    
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

<details><summary><code>client.workflow_deployments.<a href="src/vellum/resources/workflow_deployments/client.py">retrieve_workflow_release_tag</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a Workflow Release Tag by tag name, associated with a specified Workflow Deployment.
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.workflow_deployments.retrieve_workflow_release_tag(
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

**id:** `str` — Either the Workflow Deployment's ID or its unique name
    
</dd>
</dl>

<dl>
<dd>

**name:** `str` — The name of the Release Tag associated with this Workflow Deployment that you'd like to retrieve.
    
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

<details><summary><code>client.workflow_deployments.<a href="src/vellum/resources/workflow_deployments/client.py">update_workflow_release_tag</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Updates an existing Release Tag associated with the specified Workflow Deployment.
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.workflow_deployments.update_workflow_release_tag(
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

**id:** `str` — Either the Workflow Deployment's ID or its unique name
    
</dd>
</dl>

<dl>
<dd>

**name:** `str` — The name of the Release Tag associated with this Workflow Deployment that you'd like to update.
    
</dd>
</dl>

<dl>
<dd>

**history_item_id:** `typing.Optional[str]` — The ID of the Workflow Deployment History Item to tag
    
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

## ReleaseReviews
<details><summary><code>client.release_reviews.<a href="src/vellum/resources/release_reviews/client.py">retrieve_workflow_deployment_release</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a specific Workflow Deployment Release by either its UUID or the name of a Release Tag that points to it.
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.release_reviews.retrieve_workflow_deployment_release(
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

**id:** `str` — Either the Workflow Deployment's ID or its unique name
    
</dd>
</dl>

<dl>
<dd>

**release_id_or_release_tag:** `str` — Either the UUID of Workflow Deployment Release you'd like to retrieve, or the name of a Release Tag that's pointing to the Workflow Deployment Release you'd like to retrieve.
    
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

## WorkflowExecutions
<details><summary><code>client.workflow_executions.<a href="src/vellum/resources/workflow_executions/client.py">retrieve_workflow_execution_detail</a>(...)</code></summary>
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.workflow_executions.retrieve_workflow_execution_detail(
    execution_id="execution_id",
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

**execution_id:** `str` 
    
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

## WorkflowSandboxes
<details><summary><code>client.workflow_sandboxes.<a href="src/vellum/resources/workflow_sandboxes/client.py">deploy_workflow</a>(...)</code></summary>
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.workflow_sandboxes.deploy_workflow(
    id="id",
    workflow_id="workflow_id",
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

**id:** `str` — A UUID string identifying this workflow sandbox.
    
</dd>
</dl>

<dl>
<dd>

**workflow_id:** `str` — An ID identifying the Workflow you'd like to deploy.
    
</dd>
</dl>

<dl>
<dd>

**workflow_deployment_id:** `typing.Optional[str]` — The Vellum-generated ID of the Workflow Deployment you'd like to update. Cannot specify both this and workflow_deployment_name. Leave null to create a new Workflow Deployment.
    
</dd>
</dl>

<dl>
<dd>

**workflow_deployment_name:** `typing.Optional[str]` — The unique name of the Workflow Deployment you'd like to either create or update. Cannot specify both this and workflow_deployment_id. If provided and matches an existing Workflow Deployment, that Workflow Deployment will be updated. Otherwise, a new Prompt Deployment will be created.
    
</dd>
</dl>

<dl>
<dd>

**label:** `typing.Optional[str]` — In the event that a new Workflow Deployment is created, this will be the label it's given.
    
</dd>
</dl>

<dl>
<dd>

**release_tags:** `typing.Optional[typing.Sequence[str]]` — Optionally provide the release tags that you'd like to be associated with the latest release of the created/updated Prompt Deployment.
    
</dd>
</dl>

<dl>
<dd>

**release_description:** `typing.Optional[str]` — Optionally provide a description that details what's new in this Release.
    
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

<details><summary><code>client.workflow_sandboxes.<a href="src/vellum/resources/workflow_sandboxes/client.py">list_workflow_sandbox_examples</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List Workflow Sandbox examples that were previously cloned into the User's Workspace
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.workflow_sandboxes.list_workflow_sandbox_examples()

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

**tag:** `typing.Optional[ListWorkflowSandboxExamplesRequestTag]` 
    
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

## Workflows
## WorkspaceSecrets
<details><summary><code>client.workspace_secrets.<a href="src/vellum/resources/workspace_secrets/client.py">retrieve</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Used to retrieve a Workspace Secret given its ID or name.
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.workspace_secrets.retrieve(
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

**id:** `str` — Either the Workspace Secret's ID or its unique name
    
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

<details><summary><code>client.workspace_secrets.<a href="src/vellum/resources/workspace_secrets/client.py">partial_update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Used to update a Workspace Secret given its ID or name.
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.workspace_secrets.partial_update(
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

**id:** `str` — Either the Workspace Secret's ID or its unique name
    
</dd>
</dl>

<dl>
<dd>

**label:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**value:** `typing.Optional[str]` 
    
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

## Workspaces
<details><summary><code>client.workspaces.<a href="src/vellum/resources/workspaces/client.py">workspace_identity</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieves information about the active Workspace
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
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)
client.workspaces.workspace_identity()

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

