# This file was auto-generated by Fern from our API Definition.

import typing
from .string_chat_message_content_request import StringChatMessageContentRequest
from .function_call_chat_message_content_request import FunctionCallChatMessageContentRequest
from .image_chat_message_content_request import ImageChatMessageContentRequest
from .audio_chat_message_content_request import AudioChatMessageContentRequest
from .document_chat_message_content_request import DocumentChatMessageContentRequest

ArrayChatMessageContentItemRequest = typing.Union[
    StringChatMessageContentRequest,
    FunctionCallChatMessageContentRequest,
    ImageChatMessageContentRequest,
    AudioChatMessageContentRequest,
    DocumentChatMessageContentRequest,
]
