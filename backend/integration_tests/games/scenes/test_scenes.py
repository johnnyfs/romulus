import httpx
import pytest


@pytest.mark.asyncio
async def test_create_and_delete_scene(base_url: str):
    """
    Integration test that creates a game, creates a scene for it, then deletes both.

    This test hits the actual running API server (not using FastAPI TestClient).
    Make sure the server is running at localhost:8000 before running this test.
    """
    async with httpx.AsyncClient(base_url=base_url) as client:
        # First, create a game
        game_response = await client.post(
            "/api/v1/games",
            json={"name": "Test Game for Scenes"},
        )
        assert game_response.status_code == 200, f"Failed to create game: {game_response.text}"
        game = game_response.json()
        game_id = game["id"]
        print(f"Created game with ID: {game_id}")

        # Create a scene for the game
        scene_data = {
            "game_id": game_id,
            "name": "Test Scene",
            "scene_data": {
                "background_color": {"index": 0},
                "background_palettes": [
                    {"colors": [{"index": 1}, {"index": 2}, {"index": 3}]},
                    {"colors": [{"index": 4}, {"index": 5}, {"index": 6}]},
                    {"colors": [{"index": 7}, {"index": 8}, {"index": 9}]},
                    {"colors": [{"index": 10}, {"index": 11}, {"index": 12}]},
                ],
                "sprite_palettes": [
                    {"colors": [{"index": 13}, {"index": 14}, {"index": 15}]},
                    {"colors": [{"index": 16}, {"index": 17}, {"index": 18}]},
                    {"colors": [{"index": 19}, {"index": 20}, {"index": 21}]},
                    {"colors": [{"index": 22}, {"index": 23}, {"index": 24}]},
                ],
            },
        }

        create_scene_response = await client.post(
            f"/api/v1/games/{game_id}/scenes",
            json=scene_data,
        )
        assert create_scene_response.status_code == 200, f"Failed to create scene: {create_scene_response.text}"

        created_scene = create_scene_response.json()
        assert "id" in created_scene
        assert created_scene["name"] == "Test Scene"
        assert created_scene["game_id"] == game_id

        scene_id = created_scene["id"]
        print(f"Created scene with ID: {scene_id}")

        # Delete the scene
        delete_scene_response = await client.delete(f"/api/v1/games/{game_id}/scenes/{scene_id}")
        assert delete_scene_response.status_code == 200, f"Failed to delete scene: {delete_scene_response.text}"

        deleted_scene = delete_scene_response.json()
        assert deleted_scene["id"] == scene_id
        print(f"Deleted scene with ID: {scene_id}")

        # Delete the game
        delete_game_response = await client.delete(f"/api/v1/games/{game_id}")
        assert delete_game_response.status_code == 200, f"Failed to delete game: {delete_game_response.text}"

        deleted_game = delete_game_response.json()
        assert deleted_game["id"] == game_id
        print(f"Deleted game with ID: {game_id}")


@pytest.mark.asyncio
async def test_scene_validates_nesscene_schema(base_url: str):
    """Test that scene creation validates NESScene schema properly."""
    async with httpx.AsyncClient(base_url=base_url) as client:
        # Create a game first
        game_response = await client.post(
            "/api/v1/games",
            json={"name": "Test Game"},
        )
        game_id = game_response.json()["id"]

        # Try to create a scene with invalid data (missing required fields)
        invalid_scene_data = {
            "game_id": game_id,
            "name": "Invalid Scene",
            "scene_data": {
                "background_color": {"index": 0},
                # Missing background_palettes and sprite_palettes
            },
        }

        create_response = await client.post(
            f"/api/v1/games/{game_id}/scenes",
            json=invalid_scene_data,
        )
        # Should fail validation
        assert create_response.status_code == 422

        # Clean up
        await client.delete(f"/api/v1/games/{game_id}")
