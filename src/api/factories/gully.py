"""Factory classes for creating Gully-related response objects."""

from src.api.factories.base import ResponseFactory
from src.api.schemas import GullyResponse, GullyParticipantResponse
from src.db.models import Gully, GullyParticipant


class GullyFactory(ResponseFactory[Gully, GullyResponse]):
    """Factory for creating Gully response objects."""

    response_model = GullyResponse


class GullyParticipantFactory(
    ResponseFactory[GullyParticipant, GullyParticipantResponse]
):
    """Factory for creating GullyParticipant response objects."""

    response_model = GullyParticipantResponse
