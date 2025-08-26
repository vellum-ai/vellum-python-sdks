# Trust Center Q&A Workflow

A Vellum workflow example that demonstrates how to build a question-answering system using chat history and search results.

## Overview

This workflow processes user questions by:
1. Extracting the most recent message from chat history
2. Performing search operations to find relevant information
3. Formatting search results and generating answers
4. Outputting structured responses including search results, questions, and answers

## Features

- **Zero-config monitoring**: Automatically displays monitoring URLs for workflow execution
- **Local SDK integration**: Uses Vellum's local SDK for development and testing
- **Structured outputs**: Provides search results, user questions, and generated answers
- **Real-time monitoring**: View workflow execution details in the Vellum dashboard

## Requirements

- Python 3.9+
- Vellum API key (`VELLUM_API_KEY` environment variable)

## Quick Start

1. **Set your API key:**
   ```bash
   export VELLUM_API_KEY="your-api-key"
   ```

2. **Run the demo:**
   ```bash
   python -m trust_center_q_a.external
   ```

3. **View results:**
   - The script will output workflow results to the console
   - A monitoring URL will be displayed for viewing execution details in Vellum
