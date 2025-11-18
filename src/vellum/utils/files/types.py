"""Type definitions for Vellum files."""

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from vellum.client.types.vellum_audio import VellumAudio
    from vellum.client.types.vellum_document import VellumDocument
    from vellum.client.types.vellum_image import VellumImage
    from vellum.client.types.vellum_video import VellumVideo

VellumFileTypes = Union["VellumDocument", "VellumImage", "VellumVideo", "VellumAudio"]
