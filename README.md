# Romulus

A NES game development platform with a web-based editor and real-time ROM compilation.

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.13+ (for backend development without Docker)

### Running with Docker (Recommended)

1. **Copy the environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Start all services**:
   ```bash
   docker compose up --watch
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - PostgreSQL: localhost:5432

### Manual Development Setup

#### Backend

```bash
cd backend

# Install dependencies
uv pip install -e .

# Run migrations
uv run alembic upgrade head

# Start the server
uv run uvicorn main:app --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

## Configuration

### Environment Variables

All configuration is managed through environment variables defined in the root `.env` file. Copy `.env.example` to `.env` and customize as needed.

#### Port Configuration

The default ports are:
- `FRONTEND_PORT=3000` - Frontend development server
- `BACKEND_PORT=8000` - Backend API server
- `POSTGRES_PORT=5432` - PostgreSQL database

**Running Multiple Instances Concurrently**:

To run multiple instances of Romulus without port conflicts, create a custom `.env` file:

```bash
# .env
FRONTEND_PORT=3001
BACKEND_PORT=8001
POSTGRES_PORT=5433

# Update these to match your new ports
REACT_APP_API_URL=http://localhost:8001
FRONTEND_URL=http://localhost:3001
```

Then start Docker Compose, which will automatically read your `.env` file:

```bash
docker compose up --watch
```

#### Database Configuration

- `POSTGRES_USER` - PostgreSQL username (default: `romulus`)
- `POSTGRES_PASSWORD` - PostgreSQL password (default: `romulus`)
- `POSTGRES_DB` - Database name (default: `romulus`)
- `DATABASE_URL` - Full database connection string

#### Application Configuration

- `REACT_APP_API_URL` - Backend API URL for the frontend (default: `http://localhost:8000`)
- `FRONTEND_URL` - Frontend URL for CORS configuration (default: `http://localhost:3000`)
- `DEBUG` - Enable debug mode (default: `false`)

### Frontend-Only Configuration

The frontend uses a `.env` file in the `frontend/` directory:

```bash
# frontend/.env
PORT=3000
```

This file is automatically created but can be customized if running the frontend standalone.

## Project Structure

```
romulus/
├── backend/                # FastAPI backend
│   ├── api/               # API routes, schemas, and models
│   │   └── games/         # Games API
│   │       ├── components/  # Component management
│   │       └── scenes/      # Scene management
│   ├── core/              # Core utilities and ROM generation
│   ├── alembic/           # Database migrations
│   └── tests/             # Unit and integration tests
├── frontend/              # React frontend
│   └── src/
│       ├── components/    # React components
│       ├── pages/         # Page components
│       └── client/        # Generated API client
└── assets/                # Game assets (sprites, etc.)
```

## Development Workflow

### Backend API Structure

The backend follows a clean, hierarchical structure:
- `backend/api/games/routers.py` - Game endpoints
- `backend/api/games/schemas.py` - Request/response models
- `backend/api/games/models.py` - Database ORM models
- Nested resources follow the same pattern (scenes, components)

### Generating TypeScript Client

After making changes to the backend API:

```bash
# Make sure the backend is running
./generate-client.sh
```

This will generate TypeScript types and API client code in `frontend/src/client/`.

### Database Migrations

```bash
cd backend

# Create a new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1
```

### Running Tests

```bash
# Backend tests
cd backend
uv run pytest

# Backend integration tests (requires running server)
uv run pytest integration_tests/

# Frontend tests
cd frontend
npm test
```

## Docker Compose Services

- **postgres** - PostgreSQL 16 database
- **api** - FastAPI backend with hot-reload

The `docker compose --watch` mode automatically syncs code changes to the containers without rebuilding.

## Troubleshooting

### Port Already in Use

If you get a port conflict error:

```bash
# Find the process using the port
lsof -i :8000  # or :3000, :5432

# Kill the process
kill -9 <PID>
```

Or change the port in your `.env` file.

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker compose ps

# Restart the database
docker compose restart postgres

# View logs
docker compose logs postgres
```

### Reset Database

```bash
# Stop services
docker compose down

# Remove the database volume
docker volume rm romulus_postgres_data

# Start fresh
docker compose up --watch
```

## Documentation

- [Backend Development Guide](backend/DEVELOPMENT.md)
- [Frontend README](frontend/README.md)
- [Integration Tests README](backend/integration_tests/README.md)

## License

[Add your license here]
