# GitHub Actions Evaluation Example

This example demonstrates how to create an automated evaluation pipeline using GitHub Actions that:

1. Pushes a Vellum workflow to the platform
2. Upserts test cases from JSON files
3. Runs evaluations using the VellumTestSuite
4. Reports back results

## Structure

- `oracle` - Main workflow definition, a simple question and answering bot
- `test_cases/` - JSON files containing test cases
- `eval.py` - Main evaluation script
- `.github/workflows/eval.yml` - GitHub Action workflow
- `pyproject.toml` - Project configuration
- `vellum.lock.json` - Vellum workspace configuration

## Usage

We recommend copying this directory as a new project.

### Local Development

```bash
# Install dependencies
uv sync

# Run evaluation locally
uv run python eval.py
```

### GitHub Actions

The evaluation runs automatically on:

- Push to main branch
- Pull requests

## Configuration

Set the `VELLUM_API_KEY` secret in your GitHub repository settings at `https://github.com/{owner}/{repo}/settings/secrets/actions`.
