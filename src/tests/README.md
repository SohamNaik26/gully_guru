# GullyGuru API Tests

This directory contains tests for the GullyGuru API.

## Structure

- `conftest.py`: Common fixtures and test configuration
- `utils/`: Test utilities and mock factories
- `api/`: API endpoint tests

## Running Tests

To run all tests:

```bash
# From project root
pytest

# With coverage report
pytest --cov=src --cov-report=term-missing
```

To run specific test files:

```bash
# Run only gully tests
pytest src/tests/api/test_gullies.py

# Run specific test by name
pytest src/tests/api/test_gullies.py::test_get_all_gullies
```

## Writing New Tests

When writing new tests:

1. Use the existing mock utilities in `utils/` directory
2. Follow the same pattern: setup mock data, configure mocks, make request, verify response
3. Add comprehensive test cases for happy paths and error scenarios
4. Ensure tests are deterministic (no reliance on external state)

## Test Coverage

The test suite is designed to achieve 100% API route coverage. Each endpoint should have tests for:

- Successful responses
- Error cases 
- Edge cases
- Permission and authorization scenarios

If you add new API endpoints, please ensure they're covered with appropriate tests. 