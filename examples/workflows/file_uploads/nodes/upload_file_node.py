from typing import List

from vellum import VellumImage
from vellum.utils.files import upload_vellum_file
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.state import BaseState

from ..inputs import Inputs


class UploadFileNode(BaseNode[BaseState]):
    """
    Uploads files to Vellum's internal storage.

    This demonstrates how to convert public URLs or base64 data URLs into private
    vellum:uploaded-file:* URIs that can be used securely within workflows.
    """

    images = Inputs.images

    class Display(BaseNode.Display):
        icon = "vellum:icon:cloud-upload"
        color = "blue"

    class Outputs(BaseNode.Outputs):
        receipt: VellumImage
        four_pillars: VellumImage

    def run(self) -> BaseNode.Outputs:
        # Get images from inputs
        images = self.images or []

        if len(images) < 2:
            raise ValueError("Expected at least 2 images")

        # Upload each file to Vellum if it's not already uploaded
        # This will:
        # 1. Return as-is if already a vellum:uploaded-file:* URI
        # 2. Upload from base64 data URL if that's the source
        # 3. Download from URL and upload if it's a public URL
        uploaded_receipt = upload_vellum_file(
            images[0],
            filename="receipt.jpeg",
            vellum_client=self._context.vellum_client,
        )
        uploaded_four_pillars = upload_vellum_file(
            images[1],
            filename="four_pillars.png",
            vellum_client=self._context.vellum_client,
        )

        print(f"Uploaded receipt: {uploaded_receipt.src}")
        print(f"Uploaded four pillars: {uploaded_four_pillars.src}")

        return self.Outputs(
            receipt=uploaded_receipt,
            four_pillars=uploaded_four_pillars,
        )
