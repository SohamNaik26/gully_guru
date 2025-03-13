"""Factory classes for creating Fantasy-related response objects."""

from src.api.factories.base import ResponseFactory
from src.api.schemas.fantasy import (
    DraftPlayerResponse,
    DraftSquadResponse,
    SubmissionStatusResponse,
    AuctionStartResponse,
    ContestPlayerResponse,
)


class DraftPlayerResponseFactory(ResponseFactory[dict, DraftPlayerResponse]):
    """Factory for creating DraftPlayerResponse objects."""

    response_model = DraftPlayerResponse


class DraftSquadResponseFactory(ResponseFactory[dict, DraftSquadResponse]):
    """Factory for creating DraftSquadResponse objects."""

    response_model = DraftSquadResponse


class SubmissionStatusResponseFactory(ResponseFactory[dict, SubmissionStatusResponse]):
    """Factory for creating SubmissionStatusResponse objects."""

    response_model = SubmissionStatusResponse


class AuctionStartResponseFactory(ResponseFactory[dict, AuctionStartResponse]):
    """Factory for creating AuctionStartResponse objects."""

    response_model = AuctionStartResponse


class ContestPlayerResponseFactory(ResponseFactory[dict, ContestPlayerResponse]):
    """Factory for creating ContestPlayerResponse objects."""

    response_model = ContestPlayerResponse
