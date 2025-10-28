import httpx
import pytest


@pytest.mark.asyncio
async def test_create_and_get_compiled_asset(base_url: str):
    """
    Integration test that creates a compiled asset and retrieves it.

    This test hits the actual running API server (not using FastAPI TestClient).
    Make sure the server is running at localhost:8000 before running this test.
    """
    async with httpx.AsyncClient(base_url=base_url) as client:
        # Create a compiled palette asset
        palette_data = {
            "name": "test_palette",
            "type": "palette",
            "data": {
                "type": "palette",
                "palettes": [
                    {"colors": [{"index": 1}, {"index": 2}, {"index": 3}]},
                    {"colors": [{"index": 4}, {"index": 5}, {"index": 6}]},
                ],
            },
        }

        create_response = await client.post(
            "/api/v1/assets/compiled",
            json=palette_data,
        )
        assert create_response.status_code == 200, f"Failed to create compiled asset: {create_response.text}"

        created_asset = create_response.json()
        assert "id" in created_asset
        assert created_asset["name"] == "test_palette"
        assert created_asset["type"] == "palette"
        assert created_asset["data"]["type"] == "palette"
        assert len(created_asset["data"]["palettes"]) == 2

        asset_id = created_asset["id"]
        print(f"Created compiled asset with ID: {asset_id}")

        # Get the compiled asset by ID
        get_response = await client.get(f"/api/v1/assets/compiled/{asset_id}")
        assert get_response.status_code == 200, f"Failed to get compiled asset: {get_response.text}"

        retrieved_asset = get_response.json()
        assert retrieved_asset["id"] == asset_id
        assert retrieved_asset["name"] == "test_palette"
        assert retrieved_asset["type"] == "palette"

        # Delete the compiled asset
        delete_response = await client.delete(f"/api/v1/assets/compiled/{asset_id}")
        assert delete_response.status_code == 200, f"Failed to delete compiled asset: {delete_response.text}"

        deleted_asset = delete_response.json()
        assert deleted_asset["id"] == asset_id
        print(f"Deleted compiled asset with ID: {asset_id}")


@pytest.mark.asyncio
async def test_list_compiled_assets(base_url: str):
    """Test listing all compiled assets."""
    import uuid
    async with httpx.AsyncClient(base_url=base_url) as client:
        # Create two compiled assets with unique names
        unique_id = str(uuid.uuid4())[:8]
        palette1 = {
            "name": f"palette_1_{unique_id}",
            "type": "palette",
            "data": {
                "type": "palette",
                "palettes": [{"colors": [{"index": 1}, {"index": 2}, {"index": 3}]}],
            },
        }

        palette2 = {
            "name": f"palette_2_{unique_id}",
            "type": "palette",
            "data": {
                "type": "palette",
                "palettes": [{"colors": [{"index": 4}, {"index": 5}, {"index": 6}]}],
            },
        }

        create_response1 = await client.post("/api/v1/assets/compiled", json=palette1)
        assert create_response1.status_code == 200
        asset1_id = create_response1.json()["id"]

        create_response2 = await client.post("/api/v1/assets/compiled", json=palette2)
        assert create_response2.status_code == 200
        asset2_id = create_response2.json()["id"]

        # List all compiled assets
        list_response = await client.get("/api/v1/assets/compiled/")
        assert list_response.status_code == 200
        assets = list_response.json()

        # Should contain at least our two assets
        asset_ids = [asset["id"] for asset in assets]
        assert asset1_id in asset_ids
        assert asset2_id in asset_ids

        # Clean up
        await client.delete(f"/api/v1/assets/compiled/{asset1_id}")
        await client.delete(f"/api/v1/assets/compiled/{asset2_id}")


@pytest.mark.asyncio
async def test_compiled_asset_unique_constraint(base_url: str):
    """Test that the unique constraint on (name, type) is enforced."""
    async with httpx.AsyncClient(base_url=base_url) as client:
        # Create a compiled asset
        palette_data = {
            "name": "duplicate_palette",
            "type": "palette",
            "data": {
                "type": "palette",
                "palettes": [{"colors": [{"index": 1}, {"index": 2}, {"index": 3}]}],
            },
        }

        create_response1 = await client.post("/api/v1/assets/compiled", json=palette_data)
        assert create_response1.status_code == 200
        asset_id = create_response1.json()["id"]

        # Try to create another compiled asset with same name and type
        create_response2 = await client.post("/api/v1/assets/compiled", json=palette_data)
        # Should fail due to unique constraint
        assert create_response2.status_code == 500  # Database constraint violation

        # Clean up
        await client.delete(f"/api/v1/assets/compiled/{asset_id}")


@pytest.mark.asyncio
async def test_get_nonexistent_compiled_asset_returns_404(base_url: str):
    """Test that getting a non-existent compiled asset returns 404."""
    async with httpx.AsyncClient(base_url=base_url) as client:
        fake_asset_id = "00000000-0000-0000-0000-000000000000"
        get_response = await client.get(f"/api/v1/assets/compiled/{fake_asset_id}")
        assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_compiled_asset_returns_404(base_url: str):
    """Test that deleting a non-existent compiled asset returns 404."""
    async with httpx.AsyncClient(base_url=base_url) as client:
        fake_asset_id = "00000000-0000-0000-0000-000000000000"
        delete_response = await client.delete(f"/api/v1/assets/compiled/{fake_asset_id}")
        assert delete_response.status_code == 404
