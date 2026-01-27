from enum import Enum

from vellum.client.core.pydantic_utilities import UniversalBaseModel


class MLModelHostingInterface(str, Enum):
    """
    Enum representing the hosting interface for ML models.
    This will be replaced by a generated enum from the client in the future.
    """

    ANTHROPIC = "ANTHROPIC"
    AWS_BEDROCK = "AWS_BEDROCK"
    AZURE_OPENAI = "AZURE_OPENAI"
    COHERE = "COHERE"
    FIREWORKS = "FIREWORKS"
    GOOGLE = "GOOGLE"
    GROQ = "GROQ"
    MISTRAL = "MISTRAL"
    OPENAI = "OPENAI"


class MLModel(UniversalBaseModel):
    """
    Represents an ML model with its name and hosting interface.
    """

    name: str
    hosted_by: MLModelHostingInterface
