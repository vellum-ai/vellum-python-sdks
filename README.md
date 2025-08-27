<p align="center">
   <a href="https://vellum.ai">
    <picture>
      <img alt="Vellum README banner" src="https://storage.googleapis.com/vellum-public/assets/github-readme-banner.png" height="128">
    </picture>
  </a>
  <p align="center">
    <a href="https://vellum.ai">Learn more</a>
    ·
    <a href="https://www.vellum.ai/landing-pages/request-demo">Talk to us</a>
  </p>
</p>

<p align="center">
  <a href="https://pepy.tech/project/vellum-ai">
    <img src="https://img.shields.io/pypi/dm/vellum-ai" alt="Vellum AI PyPI - Downloads" >
  </a>
  <a href="https://pypi.org/project/vellum-ai" target="_blank">
    <img src="https://img.shields.io/pypi/v/vellum-ai?color=%2334D058&label=pypi%20package" alt="Package version">
  </a>
  <a href="https://www.ycombinator.com/companies/vellum">
    <img src="https://img.shields.io/badge/Y%20Combinator-W23-orange?style=flat-square" alt="Y Combinator S24">
  </a>
</p>

# Introduction

[Vellum](https://www.vellum.ai/) is the end-to-end development platform for building production-grade AI applications.

### Core Features

- **Orchestration:** A powerful SDK and IDE for defining and debugging the control flow of your AI applications
- **Prompting:** A best-in-class prompt playground for iterating on and refining prompts between models from any provider
- **Evaluations**: An evaluations framework that makes it easy to measure the quality of your AI systems at scale
- **Retrieval:** A ready-to-go service for turning unstructured content into intelligent, context-aware solutions
  optimized for AI systems
- **Deployment:** Decouple updates to your AI systems from your application code with an easy integration +
  one-click deploy
- **Observability:** Monitor and debug your AI systems in real-time with detailed logs, metrics, and end-user feedback

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

## Open-Source vs. Paid

This repo is available under the [MIT expat license](https://github.com/vellum-ai/vellum-python-sdks/blob/main/LICENSE), except
for the `ee` directory (which has its [license here](https://github.com/vellum-ai/vellum-python-sdks/blob/main/ee/LICENSE)) if applicable.

To learn more, [book a demo](https://www.vellum.ai/landing-pages/request-demo) or see our [pricing page](https://www.vellum.ai/pricing).
