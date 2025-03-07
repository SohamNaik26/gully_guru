# GullyGuru Tests

This directory contains tests for the GullyGuru application.

## Test Structure

- `conftest.py`: Pytest configuration and fixtures
- `integrations/`: Tests for data integration modules
  - `test_kaggle.py`: Tests for Kaggle data integration
  - (more integration tests to be added)
- (more test directories to be added)

## Running Tests

### Using pytest

```bash
# Run all tests
pipenv run pytest

# Run specific test file
pipenv run pytest tests/integrations/test_kaggle.py

# Run tests with verbose output
pipenv run pytest -v

# Run tests with specific markers
pipenv run pytest -m asyncio
```

### Running Integration Tests Manually

Some integration tests can be run manually without pytest:

```bash
# Run Kaggle integration tests
pipenv run python tests/integrations/test_kaggle.py
```

## Writing Tests

### Test Naming Conventions

- Test files should be named `test_*.py`
- Test functions should be named `test_*`
- Test classes should be named `Test*`

### Async Tests

For async tests, use the `@pytest.mark.asyncio` decorator:

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is True
```

### Mocking External Services

When testing integrations with external services, consider using mocks to avoid actual API calls during testing:

```python
from unittest.mock import patch, MagicMock

def test_with_mock():
    with patch('module.external_api_call') as mock_api:
        mock_api.return_value = {'data': 'mocked_response'}
        result = function_that_calls_api()
        assert result == expected_result
``` 