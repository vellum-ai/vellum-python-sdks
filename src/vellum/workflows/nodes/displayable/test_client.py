import pytest
from typing import Annotated, Literal, Optional, Union

from pydantic import Field

from vellum.client.core.pydantic_utilities import UniversalBaseModel


class BaseFruitNode(UniversalBaseModel):
    parent: Optional["FruitNode"] = None


class AppleNode(BaseFruitNode):
    type: Literal["APPLE"] = "APPLE"


class BananaNode(BaseFruitNode):
    type: Literal["BANANA"] = "BANANA"


class CherryNode(BaseFruitNode):
    type: Literal["CHERRY"] = "CHERRY"


class DateNode(BaseFruitNode):
    type: Literal["DATE"] = "DATE"


class EggplantNode(BaseFruitNode):
    type: Literal["EGGPLANT"] = "EGGPLANT"


class FigNode(BaseFruitNode):
    type: Literal["FIG"] = "FIG"


# Define the discriminated union
FruitNode = Annotated[
    Union[
        AppleNode,
        BananaNode,
        CherryNode,
        DateNode,
        EggplantNode,
        FigNode,
    ],
    Field(discriminator="type"),
]

# Update the forward references
BaseFruitNode.model_rebuild()


@pytest.mark.timeout(5)
def test_universal_base_model__recursive_discriminated_unions():
    request_body = CherryNode(
        parent=CherryNode(
            parent=CherryNode(
                parent=CherryNode(
                    parent=CherryNode(
                        parent=CherryNode(
                            parent=CherryNode(
                                parent=CherryNode(),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )

    assert request_body.dict()
