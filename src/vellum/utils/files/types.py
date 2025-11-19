"""Type definitions for Vellum files."""

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from vellum import VellumAudio, VellumDocument, VellumImage, VellumVideo

VellumFileTypes = Union["VellumDocument", "VellumImage", "VellumVideo", "VellumAudio"]
