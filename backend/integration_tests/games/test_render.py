import httpx
import pytest


@pytest.mark.asyncio
async def test_render_game_with_default_scene(base_url: str):
    """
    Integration test that creates a default game and renders it to a NES ROM.
    """
    async with httpx.AsyncClient(base_url=base_url) as client:
        # Create a game with default flag (includes main scene)
        create_response = await client.post(
            "/api/v1/games",
            json={"name": "Render Test Game"},
            params={"default": True},
        )
        assert create_response.status_code == 200, f"Failed to create game: {create_response.text}"

        created_game = create_response.json()
        game_id = created_game["id"]
        print(f"Created game with ID: {game_id}")

        # Render the game
        render_response = await client.post(f"/api/v1/games/{game_id}/render")
        assert render_response.status_code == 200, f"Failed to render game: {render_response.text}"

        # Verify response headers
        assert render_response.headers["content-type"] == "application/octet-stream"
        assert "content-disposition" in render_response.headers
        assert f"game_{game_id}.nes" in render_response.headers["content-disposition"]

        # Verify ROM structure
        rom_bytes = render_response.content
        print(f"ROM size: {len(rom_bytes)} bytes")

        # Check iNES header
        assert rom_bytes[0:4] == b"NES\x1a", "ROM should have valid iNES header"

        # Check expected ROM size: 16 byte header + 16KB PRG + 8KB CHR
        expected_size = 16 + (16 * 1024) + (8 * 1024)
        assert len(rom_bytes) == expected_size, f"ROM size should be {expected_size} bytes"

        # Verify PRG and CHR ROM sizes from header
        assert rom_bytes[4] == 0x01, "Should have 1x 16KB PRG ROM"
        assert rom_bytes[5] == 0x01, "Should have 1x 8KB CHR ROM"

        print("Successfully rendered ROM with valid iNES structure")

        # Clean up: delete the game
        delete_response = await client.delete(f"/api/v1/games/{game_id}")
        assert delete_response.status_code == 200, f"Failed to delete game: {delete_response.text}"
        print(f"Cleaned up game with ID: {game_id}")


@pytest.mark.asyncio
async def test_render_nonexistent_game_returns_error(base_url: str):
    """Test that rendering a non-existent game returns appropriate error."""
    async with httpx.AsyncClient(base_url=base_url) as client:
        # Try to render a game with a random UUID
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        render_response = await client.post(f"/api/v1/games/{fake_uuid}/render")

        # Should return 400 or 404
        assert render_response.status_code in [400, 404], "Should return error for non-existent game"


@pytest.mark.asyncio
async def test_render_game_without_scenes_returns_error(base_url: str):
    """Test that rendering a game without scenes returns appropriate error."""
    async with httpx.AsyncClient(base_url=base_url) as client:
        # Create a game without default flag (no scenes)
        create_response = await client.post(
            "/api/v1/games",
            json={"name": "Empty Game"},
            params={"default": False},
        )
        assert create_response.status_code == 200, f"Failed to create game: {create_response.text}"

        created_game = create_response.json()
        game_id = created_game["id"]
        print(f"Created empty game with ID: {game_id}")

        # Try to render the game (should fail - no main scene)
        render_response = await client.post(f"/api/v1/games/{game_id}/render")
        assert render_response.status_code == 400, "Should return 400 for game without main scene"

        error_data = render_response.json()
        assert "detail" in error_data, "Error response should have detail field"
        print(f"Expected error: {error_data['detail']}")

        # Clean up: delete the game
        delete_response = await client.delete(f"/api/v1/games/{game_id}")
        assert delete_response.status_code == 200, f"Failed to delete game: {delete_response.text}"
        print(f"Cleaned up game with ID: {game_id}")


@pytest.mark.asyncio
async def test_render_game_with_component(base_url: str):
    """Test rendering a game with a palette component."""
    async with httpx.AsyncClient(base_url=base_url) as client:
        # Create a game with default scene
        create_response = await client.post(
            "/api/v1/games",
            json={"name": "Game with Palette"},
            params={"default": True},
        )
        assert create_response.status_code == 200
        game_id = create_response.json()["id"]
        print(f"Created game with ID: {game_id}")

        # Add a palette component
        palette_response = await client.post(
            f"/api/v1/games/{game_id}/components",
            json={
                "name": "test_palette",
                "component_data": {
                    "type": "palette",
                    "palettes": [{"colors": [{"index": 1}, {"index": 2}, {"index": 3}]}],
                },
            },
        )
        assert palette_response.status_code == 200, f"Failed to create palette: {palette_response.text}"
        print("Added palette component")

        # Render the game
        render_response = await client.post(f"/api/v1/games/{game_id}/render")
        assert render_response.status_code == 200, f"Failed to render game: {render_response.text}"

        # Verify ROM structure
        rom_bytes = render_response.content
        assert rom_bytes[0:4] == b"NES\x1a", "ROM should have valid iNES header"

        expected_size = 16 + (16 * 1024) + (8 * 1024)
        assert len(rom_bytes) == expected_size

        print("Successfully rendered ROM with palette component")

        # Clean up
        delete_response = await client.delete(f"/api/v1/games/{game_id}")
        assert delete_response.status_code == 200
        print(f"Cleaned up game with ID: {game_id}")


@pytest.mark.asyncio
async def test_rendered_rom_has_correct_vector_table(base_url: str):
    """Test that the rendered ROM has a valid interrupt vector table."""
    async with httpx.AsyncClient(base_url=base_url) as client:
        # Create a default game
        create_response = await client.post(
            "/api/v1/games",
            json={"name": "Vector Test Game"},
            params={"default": True},
        )
        assert create_response.status_code == 200
        game_id = create_response.json()["id"]

        # Render the game
        render_response = await client.post(f"/api/v1/games/{game_id}/render")
        assert render_response.status_code == 200

        rom_bytes = render_response.content

        # Vector table is last 6 bytes of PRG ROM
        # PRG ROM starts after 16-byte header
        prg_start = 16
        prg_size = 16 * 1024
        vector_offset = prg_start + prg_size - 6

        # Extract vectors
        nmi_vector = rom_bytes[vector_offset : vector_offset + 2]
        reset_vector = rom_bytes[vector_offset + 2 : vector_offset + 4]
        irq_vector = rom_bytes[vector_offset + 4 : vector_offset + 6]

        # Verify vectors point to valid addresses in PRG ROM ($C000-$FFFF)
        nmi_addr = int.from_bytes(nmi_vector, "little")
        reset_addr = int.from_bytes(reset_vector, "little")
        irq_addr = int.from_bytes(irq_vector, "little")

        print(f"NMI vector: ${nmi_addr:04X}")
        print(f"RESET vector: ${reset_addr:04X}")
        print(f"IRQ vector: ${irq_addr:04X}")

        # All vectors should point to valid PRG ROM space ($C000-$FFFF)
        assert 0xC000 <= nmi_addr <= 0xFFFF, f"NMI vector ${nmi_addr:04X} out of range"
        assert 0xC000 <= reset_addr <= 0xFFFF, f"RESET vector ${reset_addr:04X} out of range"
        assert 0xC000 <= irq_addr <= 0xFFFF, f"IRQ vector ${irq_addr:04X} out of range"

        # Clean up
        await client.delete(f"/api/v1/games/{game_id}")
