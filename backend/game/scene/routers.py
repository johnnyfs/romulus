import uuid
from dependencies import get_db
from fastapi import APIRouter, Depends, HTTPException
from game.scene.models import Scene
from game.scene.schemas import SceneCreateRequest, SceneCreateResponse, SceneDeleteResponse
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("", response_model=SceneCreateResponse)
async def create_scene(
    game_id: uuid.UUID,
    request: SceneCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    scene = Scene(name=request.name, game_id=game_id, scene_data=request.scene_data)
    db.add(scene)
    await db.flush()  # Flush to generate the UUID
    return SceneCreateResponse(id=scene.id, game_id=scene.game_id, name=scene.name, scene_data=scene.scene_data)

@router.delete("/{scene_id}", response_model=SceneDeleteResponse)
async def delete_scene(
    game_id: uuid.UUID,
    scene_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    scene = await db.get(Scene, scene_id)
    if scene is None or scene.game_id != game_id:
        raise HTTPException(status_code=404, detail="Scene not found")
    await db.delete(scene)
    return SceneDeleteResponse(id=scene.id)