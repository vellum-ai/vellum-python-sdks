# Vellum Python Library

[![fern shield](https://img.shields.io/badge/%F0%9F%8C%BF-Built%20with%20Fern-brightgreen)](https://buildwithfern.com?utm_source=github&utm_medium=github&utm_campaign=readme&utm_source=https%3A%2F%2Fgithub.com%2Fvellum-ai%2Fvellum-python-sdks)
[![pypi](https://img.shields.io/pypi/v/vellum-ai)](https://pypi.python.org/pypi/vellum-ai)

The Vellum Python library provides convenient access to the Vellum API from Python.

## Table of Contents

- [Get Started](#get-started)
- [Client SDK](#client-sdk)
- [Workflows SDK](#workflows-sdk)
- [Contributing](#contributing)
- [Open-source vs paid](#open-source-vs-paid)

## Get Started

Most functionality within the Vellum SDK requires a Vellum account and API key. You can sign up for free [here](https://app.vellum.ai/signup?f=wsdk&utm_source=github&utm_medium=repo_readme&utm_campaign=sdk) or visit our [pricing page](https://www.vellum.ai/pricing) for paid options.

Even without a Vellum account, you can use the Workflows SDK to define the control flow of your AI systems. [Learn
more below](#workflows-sdk).

## Client SDK

The Vellum Client SDK, found within `src/vellum/client` is a low-level client used to interact directly with the Vellum API.
Learn more and get started by visiting the [Vellum Client SDK README](/src/vellum/client/README.md).

## Workflows SDK

The Vellum Workflows SDK is a high-level framework for defining and debugging the control flow of AI systems. At
it's core, it's a powerful workflow engine with syntactic sugar for declaratively defining graphs, the nodes within,
and the relationships between them.

The Workflows SDK can be used with or without a Vellum account, but a Vellum account is required to use certain
out-of-box nodes and features, including the ability to push and pull your Workflow definition to Vellum for editing
and debugging via a UI.

To learn more and get started, visit the [Vellum Workflows SDK README](/src/vellum/workflows/README.md).

## Contributing

See the [CONTRIBUTING.md](/CONTRIBUTING.md) for information on how to contribute to the Vellum SDKs.

## Documentation

API reference documentation is available [here](https://docs.vellum.ai/api-reference/overview/getting-started).

## Installation

```sh
pip install vellum-ai
```

## Reference

A full reference for this library is available [here](https://github.com/vellum-ai/vellum-python-sdks/blob/HEAD/./reference.md).

## Usage

Instantiate and use the client with the following:

```python
from vellum import Vellum
from vellum import StringInputRequest
client = Vellum(api_key="YOUR_API_KEY", )
client.execute_prompt(inputs=[StringInputRequest(name='name', value='value', )], )
```

## Async Client

The SDK also exports an `async` client so that you can make non-blocking calls to our API.

```python
from vellum import AsyncVellum
from vellum import StringInputRequest
import asyncio
client = AsyncVellum(api_key="YOUR_API_KEY", )
async def main() -> None:
    await client.execute_prompt(inputs=[StringInputRequest(name='name', value='value', )], )
asyncio.run(main())```

## Exception Handling

When the API returns a non-success status code (4xx or 5xx response), a subclass of the following error
will be thrown.

```python
from vellum.core.api_error import ApiError
try:
    client.execute_prompt(...)
except ApiError as e:
    print(e.status_code)
    print(e.body)
```

## Streaming

The SDK supports streaming responses, as well, the response will be a generator that you can loop over.

```python
from vellum import Vellum
from vellum import PromptRequestStringInput
from vellum import VellumVariable
from vellum import PromptParameters
from vellum import JinjaPromptBlock
client = Vellum(api_key="YOUR_API_KEY", )
response = client.ad_hoc.adhoc_execute_prompt_stream(ml_model='ml_model', input_values=[PromptRequestStringInput(key='key', value='value', )], input_variables=[VellumVariable(id='id', key='key', type="STRING", )], parameters=PromptParameters(), blocks=[JinjaPromptBlock(template='template', )], )
for chunk in response.data:
    yield chunk
```

## Advanced

### Access Raw Response Data

The SDK provides access to raw response data, including headers, through the `.with_raw_response` property.
The `.with_raw_response` property returns a "raw" client that can be used to access the `.headers` and `.data` attributes.

```python
from vellum import Vellum
client = Vellum(..., )
response = client.with_raw_response.execute_prompt(...)
print(response.headers)  # access the response headers
print(response.data)  # access the underlying object
with client.ad_hoc.with_raw_response.adhoc_execute_prompt_stream(...) as response:
    print(response.headers)  # access the response headers
    for chunk in response.data:
        print(chunk)  # access the underlying object(s)```

### Retries

The SDK is instrumented with automatic retries with exponential backoff. A request will be retried as long
as the request is deemed retryable and the number of retry attempts has not grown larger than the configured
retry limit (default: 2).

A request is deemed retryable when any of the following HTTP status codes is returned:

- [408](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/408) (Timeout)
- [429](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429) (Too Many Requests)
- [5XX](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500) (Internal Server Errors)

Use the `max_retries` request option to configure this behavior.

```python
client.execute_prompt(..., request_options={
    "max_retries": 1
})
```

### Timeouts

The SDK defaults to a 60 second timeout. You can configure this with a timeout option at the client or request level.

```python

from vellum import Vellum
client = Vellum(..., timeout=20.0, )

# Override timeout for a specific method
client.execute_prompt(..., request_options={
    "timeout_in_seconds": 1
})
```

### Custom Client

You can override the `httpx` client to customize it for your use-case. Some common use-cases include support for proxies
and transports.

```python
from vellum import Vellum
import httpx
client = Vellum(..., httpx_client=httpx.Client(proxies="http://my.test.proxy.example.com", transport=httpx.HTTPTransport(local_address="0.0.0.0"), ))```

## Contributing

While we value open-source contributions to this SDK, this library is generated programmatically.
Additions made directly to this library would have to be moved over to our generation code,
otherwise they would be overwritten upon the next generated release. Feel free to open a PR as
a proof of concept, but know that we will not be able to merge it as-is. We suggest opening
an issue first to discuss with us!

On the other hand, contributions to the README are always very welcome!
