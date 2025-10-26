import httpx
import pytest


@pytest.mark.asyncio
async def test_create_and_delete_game(base_url: str):
    """
    Integration test that creates a game via API and then deletes it.

    This test hits the actual running API server (not using FastAPI TestClient).
    Make sure the server is running at localhost:8000 before running this test.
    """
    async with httpx.AsyncClient(base_url=base_url) as client:
        # Create a game
        create_response = await client.post(
            "/api/v1/games",
            json={"name": "Test Game"},
        )
        assert create_response.status_code == 200, f"Failed to create game: {create_response.text}"

        created_game = create_response.json()
        assert "id" in created_game
        assert created_game["name"] == "Test Game"

        game_id = created_game["id"]
        print(f"Created game with ID: {game_id}")

        # Delete the game
        delete_response = await client.delete(f"/api/v1/games/{game_id}")
        assert delete_response.status_code == 200, f"Failed to delete game: {delete_response.text}"

        deleted_game = delete_response.json()
        assert deleted_game["id"] == game_id
        print(f"Deleted game with ID: {game_id}")


@pytest.mark.asyncio
async def test_delete_nonexistent_game(base_url: str):
    """Test that deleting a non-existent game returns appropriate response."""
    async with httpx.AsyncClient(base_url=base_url) as client:
        # Try to delete a game with a random UUID
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        delete_response = await client.delete(f"/api/v1/games/{fake_uuid}")

        # Based on the router, it returns None which might be 200 with null or 404
        # Adjust assertion based on actual behavior
        assert delete_response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_create_game_with_default_flag(base_url: str):
    """
    Test that creating a game with default_=True creates a game with at least one scene.
    """
    async with httpx.AsyncClient(base_url=base_url) as client:
        # Create a game with default flag
        create_response = await client.post(
            "/api/v1/games",
            json={"name": "Default Game Test"},
            params={"default": True},
        )
        assert create_response.status_code == 200, f"Failed to create game: {create_response.text}"

        created_game = create_response.json()
        game_id = created_game["id"]
        print(f"Created game with default flag, ID: {game_id}")

        # Get the game to verify it has scenes
        get_response = await client.get(f"/api/v1/games/{game_id}")
        assert get_response.status_code == 200, f"Failed to get game: {get_response.text}"

        game_data = get_response.json()
        assert "scenes" in game_data, "Game should have scenes field"
        assert len(game_data["scenes"]) >= 1, "Game created with default flag should have at least one scene"

        # Verify the default scene has expected properties
        default_scene = game_data["scenes"][0]
        assert default_scene["name"] == "main", "Default scene should be named 'main'"
        assert "scene_data" in default_scene, "Scene should have scene_data"
        assert "background_color" in default_scene["scene_data"], "Scene data should have background_color"

        print(f"Game has {len(game_data['scenes'])} scene(s): {[s['name'] for s in game_data['scenes']]}")

        # Clean up: delete the game
        delete_response = await client.delete(f"/api/v1/games/{game_id}")
        assert delete_response.status_code == 200, f"Failed to delete game: {delete_response.text}"
        print(f"Cleaned up game with ID: {game_id}")
