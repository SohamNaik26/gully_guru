"""Base factory classes for creating response objects from database models."""

from typing import Generic, List, Type, TypeVar

from pydantic import BaseModel
from sqlmodel import SQLModel

# Define type variables for the model and response
ModelT = TypeVar("ModelT", bound=SQLModel)
ResponseT = TypeVar("ResponseT", bound=BaseModel)


class ResponseFactory(Generic[ModelT, ResponseT]):
    """Base factory class for creating response objects from database models."""

    response_model: Type[ResponseT]

    @classmethod
    def create_response(cls, model: ModelT) -> ResponseT:
        """
        Create a response object from a database model.

        Args:
            model: The database model instance

        Returns:
            A response schema instance
        """
        return cls.response_model.model_validate(model)

    @classmethod
    def create_response_list(cls, models: List[ModelT]) -> List[ResponseT]:
        """
        Create a list of response objects from a list of database models.

        Args:
            models: List of database model instances

        Returns:
            List of response schema instances
        """
        return [cls.create_response(model) for model in models]
