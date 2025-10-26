import httpx
import pytest


@pytest.mark.asyncio
async def test_create_and_delete_component(base_url: str):
    """
    Integration test that creates a game, creates a component for it, then deletes both.

    This test hits the actual running API server (not using FastAPI TestClient).
    Make sure the server is running at localhost:8000 before running this test.
    """
    async with httpx.AsyncClient(base_url=base_url) as client:
        # First, create a game
        game_response = await client.post(
            "/api/v1/games",
            json={"name": "Test Game for Components"},
        )
        assert game_response.status_code == 200, f"Failed to create game: {game_response.text}"
        game = game_response.json()
        game_id = game["id"]
        print(f"Created game with ID: {game_id}")

        # Create a component for the game
        component_data = {
            "name": "test_palette",
            "component_data": {
                "type": "palette",
                "palettes": [
                    {"colors": [{"index": 1}, {"index": 2}, {"index": 3}]},
                    {"colors": [{"index": 4}, {"index": 5}, {"index": 6}]},
                ],
            },
        }

        create_component_response = await client.post(
            f"/api/v1/games/{game_id}/components",
            json=component_data,
        )
        assert create_component_response.status_code == 200, f"Failed to create component: {create_component_response.text}"

        created_component = create_component_response.json()
        assert "id" in created_component
        assert created_component["name"] == "test_palette"
        assert created_component["component_data"]["type"] == "palette"
        assert created_component["game_id"] == game_id

        component_id = created_component["id"]
        print(f"Created component with ID: {component_id}")

        # Delete the component
        delete_component_response = await client.delete(f"/api/v1/games/{game_id}/components/{component_id}")
        assert delete_component_response.status_code == 200, f"Failed to delete component: {delete_component_response.text}"

        deleted_component = delete_component_response.json()
        assert deleted_component["id"] == component_id
        print(f"Deleted component with ID: {component_id}")

        # Delete the game
        delete_game_response = await client.delete(f"/api/v1/games/{game_id}")
        assert delete_game_response.status_code == 200, f"Failed to delete game: {delete_game_response.text}"

        deleted_game = delete_game_response.json()
        assert deleted_game["id"] == game_id
        print(f"Deleted game with ID: {game_id}")


@pytest.mark.asyncio
async def test_component_unique_constraint(base_url: str):
    """Test that the unique constraint on (game_id, name, type) is enforced."""
    async with httpx.AsyncClient(base_url=base_url) as client:
        # Create a game first
        game_response = await client.post(
            "/api/v1/games",
            json={"name": "Test Game"},
        )
        game_id = game_response.json()["id"]

        # Create a component
        component_data = {
            "name": "duplicate_palette",
            "component_data": {
                "type": "palette",
                "palettes": [{"colors": [{"index": 1}, {"index": 2}, {"index": 3}]}],
            },
        }

        create_response1 = await client.post(
            f"/api/v1/games/{game_id}/components",
            json=component_data,
        )
        assert create_response1.status_code == 200
        component_id = create_response1.json()["id"]

        # Try to create another component with same name and type
        create_response2 = await client.post(
            f"/api/v1/games/{game_id}/components",
            json=component_data,
        )
        # Should fail due to unique constraint
        assert create_response2.status_code == 500  # Database constraint violation

        # Clean up
        await client.delete(f"/api/v1/games/{game_id}/components/{component_id}")
        await client.delete(f"/api/v1/games/{game_id}")


@pytest.mark.asyncio
async def test_delete_nonexistent_component_returns_404(base_url: str):
    """Test that deleting a non-existent component returns 404."""
    async with httpx.AsyncClient(base_url=base_url) as client:
        # Create a game first
        game_response = await client.post(
            "/api/v1/games",
            json={"name": "Test Game"},
        )
        game_id = game_response.json()["id"]

        # Try to delete a non-existent component
        fake_component_id = "00000000-0000-0000-0000-000000000000"
        delete_response = await client.delete(f"/api/v1/games/{game_id}/components/{fake_component_id}")
        assert delete_response.status_code == 404

        # Clean up
        await client.delete(f"/api/v1/games/{game_id}")


@pytest.mark.asyncio
async def test_delete_component_from_wrong_game_returns_404(base_url: str):
    """Test that deleting a component with wrong game_id returns 404."""
    async with httpx.AsyncClient(base_url=base_url) as client:
        # Create two games
        game1_response = await client.post("/api/v1/games", json={"name": "Game 1"})
        game1_id = game1_response.json()["id"]

        game2_response = await client.post("/api/v1/games", json={"name": "Game 2"})
        game2_id = game2_response.json()["id"]

        # Create a component for game 1
        component_response = await client.post(
            f"/api/v1/games/{game1_id}/components",
            json={
                "name": "palette",
                "component_data": {
                    "type": "palette",
                    "palettes": [{"colors": [{"index": 1}, {"index": 2}, {"index": 3}]}],
                },
            },
        )
        component_id = component_response.json()["id"]

        # Try to delete it using game 2's ID
        delete_response = await client.delete(f"/api/v1/games/{game2_id}/components/{component_id}")
        assert delete_response.status_code == 404

        # Clean up
        await client.delete(f"/api/v1/games/{game1_id}/components/{component_id}")
        await client.delete(f"/api/v1/games/{game1_id}")
        await client.delete(f"/api/v1/games/{game2_id}")
