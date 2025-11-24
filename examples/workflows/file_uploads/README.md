# File Uploads Example

This example demonstrates how to upload images to Vellum's internal storage and use them in vision prompts.

## Overview

This workflow shows how to:
1. Upload images from URLs or base64 to Vellum's secure storage
2. Convert them to `vellum:uploaded-file:*` URIs
3. Use the uploaded images in vision prompts

## Key Components

### `nodes/upload_file_node.py`
Uploads images using the `upload_vellum_file()` utility function. Accepts images from URLs, base64, or already-uploaded files.

### `nodes/use_uploaded_file_node.py`
Uses the uploaded images in a vision prompt. Note that `VariablePromptBlock` for images must be placed **inside** the `ChatMessagePromptBlock`'s `blocks` array.

## Running the Example

```bash
poetry run python -m examples.workflows.file_uploads.sandbox
```

## Key Points

- The `upload_vellum_file()` utility handles uploading from URLs, base64, or already-uploaded files
- Images are converted to `vellum:uploaded-file:*` URIs for secure internal use
- Multiple images require separate `VariablePromptBlock` instances (one per image)
- `VariablePromptBlock` for images must be inside `ChatMessagePromptBlock` blocks, not at the top level
