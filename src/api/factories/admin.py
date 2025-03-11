"""Factory classes for creating Admin-related response objects."""

from src.api.factories.base import ResponseFactory
from src.api.schemas import AdminRoleResponse
from src.db.models import GullyParticipant


class AdminFactory(ResponseFactory[GullyParticipant, AdminRoleResponse]):
    """Factory for creating Admin role response objects."""

    response_model = AdminRoleResponse
