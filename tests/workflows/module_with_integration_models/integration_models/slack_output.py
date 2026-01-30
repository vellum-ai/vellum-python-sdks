from pydantic import BaseModel


class SlackOutput(BaseModel):
    messages: list
