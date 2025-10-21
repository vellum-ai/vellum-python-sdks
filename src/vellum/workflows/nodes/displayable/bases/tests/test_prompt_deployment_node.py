import pytest

from vellum import (
    AudioInputRequest,
    DocumentInputRequest,
    ImageInputRequest,
    VellumAudio,
    VellumAudioRequest,
    VellumDocument,
    VellumDocumentRequest,
    VellumImage,
    VellumImageRequest,
    VellumVideo,
    VellumVideoRequest,
    VideoInputRequest,
)
from vellum.workflows.nodes import PromptDeploymentNode


@pytest.mark.parametrize(
    [
        "raw_input",
        "expected_compiled_inputs",
    ],
    [
        (
            VellumAudio(src="data:audio/wav;base64,mockaudio"),
            [AudioInputRequest(name="file_input", value=VellumAudioRequest(src="data:audio/wav;base64,mockaudio"))],
        ),
        (
            VellumImage(src="data:image/png;base64,mockimage"),
            [ImageInputRequest(name="file_input", value=VellumImageRequest(src="data:image/png;base64,mockimage"))],
        ),
        (
            VellumVideo(src="data:video/mp4;base64,mockvideo"),
            [VideoInputRequest(name="file_input", value=VellumVideoRequest(src="data:video/mp4;base64,mockvideo"))],
        ),
        (
            VellumDocument(src="mockdocument"),
            [DocumentInputRequest(name="file_input", value=VellumDocumentRequest(src="mockdocument"))],
        ),
        (
            VellumAudioRequest(src="data:audio/wav;base64,mockaudio"),
            [AudioInputRequest(name="file_input", value=VellumAudioRequest(src="data:audio/wav;base64,mockaudio"))],
        ),
        (
            VellumImageRequest(src="data:image/png;base64,mockimage"),
            [ImageInputRequest(name="file_input", value=VellumImageRequest(src="data:image/png;base64,mockimage"))],
        ),
        (
            VellumVideoRequest(src="data:video/mp4;base64,mockvideo"),
            [VideoInputRequest(name="file_input", value=VellumVideoRequest(src="data:video/mp4;base64,mockvideo"))],
        ),
        (
            VellumDocumentRequest(src="mockdocument"),
            [DocumentInputRequest(name="file_input", value=VellumDocumentRequest(src="mockdocument"))],
        ),
        (
            {"src": "https://example.com/document.pdf"},
            [
                DocumentInputRequest(
                    name="file_input", value=VellumDocumentRequest(src="https://example.com/document.pdf")
                )
            ],
        ),
        (
            {"src": "https://example.com/document.pdf", "metadata": {"author": "test"}},
            [
                DocumentInputRequest(
                    name="file_input",
                    value=VellumDocumentRequest(src="https://example.com/document.pdf", metadata={"author": "test"}),
                )
            ],
        ),
    ],
)
def test_file_input_compilation(raw_input, expected_compiled_inputs):
    """
    Tests that file inputs are correctly compiled to the appropriate input type.
    """

    class MyPromptDeploymentNode(PromptDeploymentNode):
        deployment = "test-deployment"
        prompt_inputs = {"file_input": raw_input}

    # WHEN we compile the inputs
    compiled_inputs = MyPromptDeploymentNode()._compile_prompt_inputs()

    # THEN we should get the correct input type
    assert compiled_inputs == expected_compiled_inputs
