# Vellum Python Library

[![fern shield](https://img.shields.io/badge/%F0%9F%8C%BF-Built%20with%20Fern-brightgreen)](https://buildwithfern.com?utm_source=github&utm_medium=github&utm_campaign=readme&utm_source=https%3A%2F%2Fgithub.com%2Fvellum-ai%2Fvellum-python-sdks)
[![pypi](https://img.shields.io/pypi/v/vellum-ai)](https://pypi.python.org/pypi/vellum-ai)

The Vellum Python library provides convenient access to the Vellum API from Python.

## API Docs
You can find Vellum's complete API docs at [docs.vellum.ai](https://docs.vellum.ai/api-reference/introduction/getting-started).

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

## Async Client

The SDK also exports an `async` client so that you can make non-blocking calls to our API.

```python
import asyncio

from vellum import AsyncVellum, StringInputRequest

client = AsyncVellum(
    api_version="YOUR_API_VERSION",
    api_key="YOUR_API_KEY",
)


async def main() -> None:
    await client.execute_prompt(
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


asyncio.run(main())
```

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

## Advanced

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

client = Vellum(
    ...,
    timeout=20.0,
)


# Override timeout for a specific method
client.execute_prompt(..., request_options={
    "timeout_in_seconds": 1
})
```

### Custom Client

You can override the `httpx` client to customize it for your use-case. Some common use-cases include support for proxies
and transports.

```python
import httpx
from vellum import Vellum

client = Vellum(
    ...,
    httpx_client=httpx.Client(
        proxies="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)
```

