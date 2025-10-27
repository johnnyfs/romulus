# Development Guide

## Running the Backend with Auto-Reload

The backend is configured to automatically reload when you make code changes.

### Using Docker Compose (Recommended)

1. **Start services with watch mode:**
   ```bash
   docker compose up --watch
   ```

2. **Or, if services are already running:**
   ```bash
   docker compose watch
   ```

This will:
- Start PostgreSQL and the API server
- Automatically run database migrations on startup
- Watch for file changes in your local directory
- Sync changes to the container
- Uvicorn will detect changes and reload automatically

### File Sync Behavior

- **Synced files:** All Python files (`.py`) in the project
- **Ignored:** `__pycache__/`, `.venv/`, `.pytest_cache/`, `*.pyc`
- **Rebuild trigger:** Changes to `pyproject.toml` will trigger a full rebuild

### Manual Development (Without Docker)

If you prefer to run the backend directly:

1. **Install dependencies:**
   ```bash
   uv pip install -e .
   ```

2. **Run migrations:**
   ```bash
   uv run alembic upgrade head
   ```

3. **Start the server:**
   ```bash
   uv run uvicorn main:app --reload
   ```

## Testing the Render Endpoint

Once the backend is running, you can test the ROM render endpoint:

```bash
# Create a game with default scene
GAME_ID=$(curl -s -X POST "http://localhost:8000/api/v1/games?default=true" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Game"}' | jq -r '.id')

# Render the ROM
curl -X POST "http://localhost:8000/api/v1/games/$GAME_ID/render" \
  -o game.nes

# Verify it's a valid NES ROM
file game.nes
xxd game.nes | head -5
```

You should see:
- File size: 24,592 bytes (16-byte header + 16KB PRG + 8KB CHR)
- Header: `NES\x1a` (first 4 bytes)

## Running Tests

```bash
# Run all tests
uv run pytest

# Run ROM tests specifically
uv run pytest tests/rom/ -v

# Run integration tests (requires server running)
uv run pytest integration_tests/ -v
```

## Common Issues

### Port 8000 Already in Use

If you get an error about port 8000 being in use:

```bash
# Find and kill the process
lsof -i :8000
kill -9 <PID>

# Then restart docker-compose
docker compose up --watch
```

### Database Connection Issues

If the API can't connect to the database:

```bash
# Check if PostgreSQL is running
docker compose ps

# Restart just the database
docker compose restart postgres

# View logs
docker compose logs postgres
```

### Migration Issues

If you need to reset the database:

```bash
# Stop services
docker compose down

# Remove the database volume
docker volume rm backend_postgres_data

# Start fresh
docker compose up --watch
```
