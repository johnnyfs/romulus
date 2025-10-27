# Integration Tests

## Prerequisites

Before running integration tests, ensure:

1. **Database is running**:
   ```bash
   docker compose up -d
   ```

2. **Database migrations are applied** (when you set up Alembic):
   ```bash
   alembic upgrade head
   ```

3. **FastAPI server is running**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

   Or if you have a different startup command, use that. The tests expect the API to be available at `http://localhost:8000`.

## Running Tests

From the project root:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_game_integration.py

# Run specific test
pytest tests/test_game_integration.py::test_create_and_delete_game

# Run with output from print statements
pytest -s
```

## Notes

- These are **integration tests** that hit the real API endpoint, not unit tests with mocked dependencies
- They use `httpx.AsyncClient` to make HTTP requests to the running server
- Tests create real data in the database and then clean it up by deleting it
- Make sure your local server is running before executing tests
