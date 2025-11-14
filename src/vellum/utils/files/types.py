"""Type definitions for Vellum files."""

from typing import Union

from vellum import VellumAudio, VellumDocument, VellumImage, VellumVideo

VellumFileTypes = Union[VellumDocument, VellumImage, VellumVideo, VellumAudio]
