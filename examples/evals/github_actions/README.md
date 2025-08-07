# GitHub Actions Evaluation Example

This example demonstrates how to create an automated evaluation pipeline using GitHub Actions that:

1. Pushes a Vellum workflow to the platform
2. Upserts test cases from JSON files
3. Runs evaluations using the VellumTestSuite
4. Reports back results

## Structure

- `workflow.py` - Main workflow definition
- `inputs.py` - Workflow input schema
- `nodes/` - Individual workflow nodes
- `test_cases/` - JSON files containing test cases
- `eval.py` - Main evaluation script
- `.github/workflows/eval.yml` - GitHub Action workflow
- `pyproject.toml` - Project configuration
- `vellum.lock.json` - Vellum workspace configuration

## Usage

### Local Development
```bash
# Install dependencies
poetry install

# Run evaluation locally
cd examples/evals/github_actions
poetry run python eval.py
```

### GitHub Actions
The evaluation runs automatically on:
- Push to main branch
- Pull requests
- Daily schedule (8 AM UTC)

## Configuration
Set the `VELLUM_API_KEY` secret in your GitHub repository settings.
