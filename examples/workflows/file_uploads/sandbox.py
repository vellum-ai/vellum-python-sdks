import base64
import os

from vellum import VellumImage
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .inputs import Inputs
from .workflow import Workflow

if __name__ != "__main__":
    raise Exception("This file is not meant to be imported")


# Create images from different sources
# Receipt image: From a public URL
receipt_image_url = "https://storage.googleapis.com/vellum-public/help-docs/extract-from-image-of-receipt.jpeg"

# Four pillars image: From base64 (read from local file)
current_dir = os.path.dirname(os.path.abspath(__file__))
four_pillars_image_path = os.path.join(current_dir, "vellum_four_pillars.png")
with open(four_pillars_image_path, "rb") as f:
    four_pillars_image_bytes = f.read()
four_pillars_image_base64 = base64.b64encode(four_pillars_image_bytes).decode("utf-8")
four_pillars_image_base64_src = f"data:image/png;base64,{four_pillars_image_base64}"

runner = WorkflowSandboxRunner(
    workflow=Workflow(),
    dataset=[
        Inputs(
            images=[
                VellumImage(src=receipt_image_url),
                VellumImage(src=four_pillars_image_base64_src),
            ],
        ),
    ],
)

runner.run()
