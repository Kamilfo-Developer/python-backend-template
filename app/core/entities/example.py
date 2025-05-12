"""Example entity."""

from random import randint
from typing import Self
from uuid import uuid4

from app.core.exceptions.example import ExampleBusinessLogicException
from app.types import ExampleId


class Example:
    """Example entity."""

    id: ExampleId
    name: str
    content: str

    def __init__(self, id: ExampleId, name: str, content: str) -> None:
        self.id = id
        self.name = name
        self.content = content

    def do_some_business_logic(self, name_prefix: str) -> None:
        """Do some business logic.

        Args:
            name_prefix (str): Name prefix.

        Raises:
            ExampleBusinessLogicException: If something happens in business logic.

        """

        if randint(0, 10) == 0:
            raise ExampleBusinessLogicException

        self.name = f"{name_prefix}{self.name}"

    @classmethod
    def create(cls, name: str, content: str) -> Self:
        """Create new example.

        Args:
            name (str): example name.
            content (str): example content.

        Returns:
            Self: New example entity.

        """
        return cls(id=uuid4(), name=name, content=content)
