# Backend Development Skill

You are working on the Romulus backend, a FastAPI application for building NES games.

## Project Structure

```
backend/
├── main.py              # FastAPI app entry point with CORS
├── config.py            # Settings with pydantic-settings
├── database.py          # Async SQLAlchemy setup
├── dependencies.py      # FastAPI dependencies (get_db)
├── core/
│   ├── models.py        # UUIDMixin base class
│   ├── schemas.py       # NESColor, NESPalette, NESScene
│   ├── pydantic_type.py # Custom SQLAlchemy type for Pydantic models
│   └── rom/             # NES ROM building infrastructure
├── game/
│   ├── models.py        # Game ORM model
│   ├── routers.py       # Game API endpoints
│   ├── schemas.py       # Game request/response schemas
│   └── scene/
│       ├── models.py    # Scene ORM model
│       ├── routers.py   # Scene API endpoints
│       └── schemas.py   # Scene request/response schemas
└── alembic/             # Database migrations
```

## Technology Stack

- **FastAPI** 0.115.0+
- **SQLAlchemy** 2.0+ (async with asyncpg)
- **PostgreSQL** with asyncpg driver
- **Pydantic** 2.0+ for validation
- **Alembic** for migrations

## Important Patterns

### 1. Import Conventions
**CRITICAL: Avoid imports at call sites unless absolutely required**

Bad (imports at call site):
```python
@router.get("/{game_id}")
async def get_game(game_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from fastapi import HTTPException  # ❌ Don't do this
    from sqlalchemy import select       # ❌ Don't do this
```

Good (imports at top):
```python
from fastapi import HTTPException
from sqlalchemy import select

@router.get("/{game_id}")
async def get_game(game_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    # Use imports here
```

Only use call-site imports for:
- Circular dependency resolution
- Optional dependencies
- Heavy imports that are rarely used

### 2. Async Database Pattern
All database operations use async/await:

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Simple query
stmt = select(Game)
result = await db.execute(stmt)
games = result.scalars().all()

# With eager loading
stmt = select(Game).where(Game.id == game_id).options(selectinload(Game.scenes))
result = await db.execute(stmt)
game = result.scalar_one_or_none()
```

### 3. API Response Pattern
All endpoints return Pydantic models:

```python
@router.get("/{game_id}", response_model=GameGetResponse)
async def get_game(game_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    # Query and return Pydantic model
    return GameGetResponse(id=game.id, name=game.name, scenes=scenes)
```

### 4. Dependency Injection
Use FastAPI's dependency injection:

```python
from dependencies import get_db

@router.post("")
async def create_game(
    request: GameCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    # db is injected automatically
```

### 5. Error Handling
Use HTTPException for errors:

```python
from fastapi import HTTPException

if game is None:
    raise HTTPException(status_code=404, detail="Game not found")
```

## Database Models

### UUIDMixin
All models inherit from UUIDMixin which provides:
- `id: uuid.UUID` (primary key, auto-generated)
- `created_at: datetime`
- `updated_at: datetime`

### Relationships
Use SQLAlchemy 2.0 relationship patterns:

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Game(UUIDMixin, Base):
    __tablename__ = "games"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    scenes: Mapped[list["Scene"]] = relationship(
        "Scene",
        back_populates="game",
        cascade="all, delete-orphan",
        lazy="raise"  # Force explicit loading
    )
```

## CORS Configuration

CORS is configured in main.py:
```python
from config import settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Running Migrations

```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Testing

Integration tests are in `integration_tests/`:
```bash
cd backend
pytest integration_tests/
```

## Common Tasks

### Add a new endpoint
1. Define request/response schemas in `schemas.py`
2. Add route in `routers.py` with proper imports at top
3. Use async/await for database operations
4. Return Pydantic response models

### Add a new model
1. Create model in `models.py` inheriting from UUIDMixin
2. Add relationship annotations
3. Run `alembic revision --autogenerate`
4. Review and run migration

### Update OpenAPI client
After backend schema changes:
```bash
./generate-client.sh
```

## Environment Variables

Configuration in `config.py` via pydantic-settings:
- `DATABASE_URL`: PostgreSQL connection string
- `FRONTEND_URL`: CORS allowed origin
- `DEBUG`: Debug mode flag
- `API_V1_PREFIX`: API prefix (default: /api/v1)

## Key Reminders

1. ✅ **Import at the top of files, not at call sites**
2. ✅ Use async/await for all database operations
3. ✅ Use `selectinload()` for eager loading relationships
4. ✅ Always specify `response_model` on endpoints
5. ✅ Use Pydantic for validation and serialization
6. ✅ Raise HTTPException for errors
7. ✅ Use dependency injection for database sessions
8. ✅ Follow the existing patterns in routers.py files
