import base64
import os

import dotenv

from vellum import VellumImage
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .inputs import Inputs
from .workflow import Workflow

if __name__ != "__main__":
    raise Exception("This file is not meant to be imported")

dotenv.load_dotenv()

# # Basic upload example: Upload chat.png and get vellum URI
# current_dir = os.path.dirname(os.path.abspath(__file__))
# chat_image_path = os.path.join(current_dir, "chat.png")
# with open(chat_image_path, "rb") as f:
#     chat_image_bytes = f.read()
# chat_image_base64 = base64.b64encode(chat_image_bytes).decode("utf-8")
# chat_image_base64_src = f"data:image/png;base64,{chat_image_base64}"

# uploaded_chat = VellumImage(src=chat_image_base64_src).upload(filename="chat.png")
# # vellum:uploaded-file:9cdc7745-7260-4117-bd3d-b83fd6c2b6f2
# print(f"Uploaded chat.png URI: {uploaded_chat.src}")

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
                VellumImage(src="vellum:uploaded-file:9cdc7745-7260-4117-bd3d-b83fd6c2b6f2"),  # chat.png
                VellumImage(src=receipt_image_url),
                VellumImage(src=four_pillars_image_base64_src),
            ],
        ),
    ],
)

runner.run()
