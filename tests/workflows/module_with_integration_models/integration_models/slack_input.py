from pydantic import BaseModel


class SlackInput(BaseModel):
    channel: str
