# Vellum Feature Showcase Workflow

This workflow demonstrates several advanced Vellum features by generating subtopics for a given topic and providing either a simple summary or detailed exploration based on the selected mode.

## Overview

The workflow accepts a `topic` and an optional `detailed_mode` flag. It:

1. Generates 5 subtopics for the main topic using an LLM
2. Extracts subtopics from JSON using Jinja2 templating
3. Routes based on mode: detailed (parallel exploration) or simple (brief summary)
4. Outputs the list of subtopics and a summary

## Key Features Demonstrated

- **Conditional Ports**: Route execution based on input values
- **MapNode**: Parallel processing of items with concurrency control
- **MergeBehavior**: Control how nodes wait for incoming data
- **Coalesce**: Provide fallback values from multiple sources
- **Inline Prompt Nodes**: Structured JSON output with schema validation
- **TemplatingNode**: Jinja2 templating for data extraction

## Inputs

| Name | Type | Description |
|------|------|-------------|
| `topic` | `str` | The main topic to explore |
| `detailed_mode` | `Optional[Any]` | When `True`, generates detailed explanations |

## Outputs

| Name | Type | Description |
|------|------|-------------|
| `subtopics` | `list[str]` | List of generated subtopics |
| `summary` | `str` | Summary or combined detailed explanations |
