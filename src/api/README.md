# GullyGuru API

This directory contains the API implementation for the GullyGuru application.

## Structure

The API is organized into the following components:

```
src/api/
├── client.py                 # API client factory and global instance
├── dependencies.py           # FastAPI dependencies (auth, sessions)
├── exceptions.py             # Custom API exceptions
├── factories/                # Response factories
│   ├── base.py               # Base factory class
│   ├── fantasy.py            # Fantasy-related factories
│   ├── ...                   # Other domain-specific factories
│   └── __init__.py
├── routes/                   # API route handlers
│   ├── fantasy.py            # Fantasy-related routes
│   ├── ...                   # Other domain-specific routes
│   └── __init__.py
├── schemas/                  # Pydantic models for requests/responses
│   ├── fantasy.py            # Fantasy-related schemas
│   ├── ...                   # Other domain-specific schemas
│   └── __init__.py
├── services/                 # Service clients for API operations
│   ├── base.py               # Base service classes
│   ├── fantasy.py            # Fantasy-related services
│   ├── ...                   # Other domain-specific services
│   └── __init__.py
└── __init__.py
```

## Components

### Schemas

Schemas define the data models using Pydantic:
- Used by routes for request/response validation
- Used by factories to create response objects
- Imported by services for type hints

### Services

Services contain business logic:
- `BaseService`: Base class for HTTP client services
- `BaseServiceClient`: Base class for database client services
- Domain-specific services (e.g., `FantasyService`, `FantasyServiceClient`)
- Services use schemas for type hints and data validation
- Services use factories to create response objects

### Factories

Factories create response objects:
- Convert database models or dictionaries to Pydantic response models
- Used by services to format responses
- Follow a consistent pattern with a base `ResponseFactory` class

### Routes

Routes handle HTTP requests:
- Use dependencies for auth and database sessions
- Instantiate service clients
- Call service methods to perform operations
- Return responses created by services/factories

### Client

The client module provides:
- `APIClient`: Factory for creating HTTP client services
- `api_client`: Global instance of `APIClient`
- Used by external components to access API services

## Best Practices

1. **Separation of Concerns**:
   - Routes handle HTTP requests and responses
   - Service layer contains business logic and database operations
   - Factories create response objects from database models or dictionaries

2. **Consistent Pattern**:
   - All services follow the same structure
   - All routes follow the same pattern for handling requests
   - All factories follow the same pattern for creating response objects

3. **Dependency Injection**:
   - Database session is injected into routes
   - Current user is injected into routes
   - Service is created in each route handler

4. **Type Safety**:
   - All request and response models are defined using Pydantic
   - All route handlers specify their response models
   - All service methods specify their return types

5. **Factory Usage**:
   - Services use factories to create response objects
   - Routes return responses created by services
   - Factories ensure consistent response formats

## Examples

### Creating a New Service

```python
# src/api/services/example.py
from typing import Dict, Any
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.services.base import BaseService, BaseServiceClient
from src.api.factories import ExampleFactory
from src.db.models import ExampleModel

class ExampleService(BaseService):
    """Client for interacting with example-related API endpoints."""

    def __init__(self, base_url: str, client: httpx.AsyncClient = None):
        super().__init__(base_url, client)
        self.endpoint = f"{self.base_url}/example"

    async def get_example(self, example_id: int) -> Dict[str, Any]:
        response = await self._make_request(
            "GET", f"{self.endpoint}/{example_id}"
        )
        return response

class ExampleServiceClient(BaseServiceClient):
    """Client for interacting with example-related database operations."""

    async def get_example(self, example_id: int) -> Dict[str, Any]:
        stmt = select(ExampleModel).where(ExampleModel.id == example_id)
        result = await self.db.execute(stmt)
        example = result.scalars().first()
        
        if not example:
            return {"error": "Example not found"}
            
        response_data = {
            "id": example.id,
            "name": example.name,
        }
        return ExampleFactory.create_response(response_data)
```

### Creating a New Route

```python
# src/api/routes/example.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session
from src.api.schemas.example import ExampleResponse
from src.api.services.example import ExampleServiceClient

router = APIRouter()

@router.get("/{example_id}", response_model=ExampleResponse)
async def get_example(
    example_id: int,
    db: AsyncSession = Depends(get_session),
):
    """Get an example by ID."""
    example_service = ExampleServiceClient(db)
    result = await example_service.get_example(example_id)
    return result
```

### Creating a New Factory

```python
# src/api/factories/example.py
from src.api.factories.base import ResponseFactory
from src.api.schemas.example import ExampleResponse

class ExampleFactory(ResponseFactory[dict, ExampleResponse]):
    """Factory for creating Example response objects."""

    response_model = ExampleResponse
```

### Creating a New Schema

```python
# src/api/schemas/example.py
from pydantic import BaseModel, ConfigDict

class ExampleBase(BaseModel):
    """Base schema for example information."""

    name: str

class ExampleCreate(ExampleBase):
    """Schema for creating an example."""

    model_config = ConfigDict(from_attributes=True)

class ExampleResponse(ExampleBase):
    """Response schema for example."""

    id: int

    model_config = ConfigDict(from_attributes=True)
``` 