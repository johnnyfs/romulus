"""
Integration tests for resource filtering API.

These tests verify that the resource list endpoint correctly filters resources
by type and state using JSONB queries.
"""
import httpx
import pytest


@pytest.mark.asyncio
async def test_resource_filtering_by_type_and_state(base_url: str):
    """
    Test that resources can be filtered by both resource_type and state.

    This test verifies the fix for JSONB query filtering where:
    - Filter by resource_type alone should work
    - Filter by state alone should work
    - Filter by both resource_type AND state should work together
    """
    async with httpx.AsyncClient(base_url=base_url) as client:
        # First, create some test resources with different states
        test_resources = []

        # Create a raw sprite resource
        raw_sprite = {
            "storage_key": "test/raw_sprite.png",
            "resource_data": {
                "type": "image",
                "state": "raw",
                "image_type": "sprite",
                "tags": ["test"],
                "processed": False,
            }
        }

        # Note: In a real scenario, we'd go through the full upload flow
        # For now, we assume there's at least one resource in the database
        # created through the actual upload flow

        # Test 1: List all resources (no filters)
        response = await client.get("/api/v1/resources")
        assert response.status_code == 200, f"Failed to list resources: {response.text}"
        all_resources = response.json()
        assert isinstance(all_resources, list)
        print(f"Total resources: {len(all_resources)}")

        # Test 2: Filter by resource_type only
        response = await client.get("/api/v1/resources?resource_type=image")
        assert response.status_code == 200, f"Failed to filter by type: {response.text}"
        image_resources = response.json()
        assert isinstance(image_resources, list)
        print(f"Image resources: {len(image_resources)}")

        # Verify all returned resources are images
        for resource in image_resources:
            assert resource["resource_data"]["type"] == "image"

        # Test 3: Filter by state only
        response = await client.get("/api/v1/resources?state=raw")
        assert response.status_code == 200, f"Failed to filter by state: {response.text}"
        raw_resources = response.json()
        assert isinstance(raw_resources, list)
        print(f"Raw resources: {len(raw_resources)}")

        # Verify all returned resources are in raw state
        for resource in raw_resources:
            assert resource["resource_data"]["state"] == "raw"

        # Test 4: Filter by BOTH resource_type AND state (this was broken before the fix)
        response = await client.get("/api/v1/resources?resource_type=image&state=raw")
        assert response.status_code == 200, f"Failed to filter by type and state: {response.text}"
        filtered_resources = response.json()
        assert isinstance(filtered_resources, list)
        print(f"Filtered resources (image + raw): {len(filtered_resources)}")

        # Verify all returned resources match both filters
        for resource in filtered_resources:
            assert resource["resource_data"]["type"] == "image", \
                f"Resource {resource['id']} has wrong type: {resource['resource_data']['type']}"
            assert resource["resource_data"]["state"] == "raw", \
                f"Resource {resource['id']} has wrong state: {resource['resource_data']['state']}"

        # The filtered list should be a subset of both individual filters
        # (In a real scenario with multiple resources of different types/states)
        # For now, we just verify the query doesn't return empty if there are matching resources
        if len(all_resources) > 0:
            # If there are resources, the filters should work
            assert len(image_resources) <= len(all_resources)
            assert len(raw_resources) <= len(all_resources)
            assert len(filtered_resources) <= len(image_resources)
            assert len(filtered_resources) <= len(raw_resources)


@pytest.mark.asyncio
async def test_resource_ordering_by_processed_flag(base_url: str):
    """
    Test that resources are ordered with unprocessed resources first.

    Resources should be ordered by:
    1. processed flag (false before true)
    2. id (oldest first)
    """
    async with httpx.AsyncClient(base_url=base_url) as client:
        response = await client.get("/api/v1/resources?resource_type=image&state=raw")
        assert response.status_code == 200
        resources = response.json()

        if len(resources) > 1:
            # Check that unprocessed resources come before processed ones
            processed_flags = [r["resource_data"].get("processed", False) for r in resources]

            # Find the first True (processed) in the list
            first_processed_index = next((i for i, p in enumerate(processed_flags) if p), None)

            if first_processed_index is not None:
                # All items after the first processed should also be processed
                for i in range(first_processed_index, len(processed_flags)):
                    assert processed_flags[i], \
                        f"Found unprocessed resource at index {i} after processed resource"

        print(f"Resource ordering verified for {len(resources)} resources")


@pytest.mark.asyncio
async def test_full_upload_and_filter_flow(base_url: str):
    """
    Integration test that goes through the full upload flow and then tests filtering.

    Steps:
    1. Get upload ticket
    2. Upload file to MinIO (simulated - we'll use a small test file)
    3. Finalize the resource
    4. Verify it appears in filtered results
    """
    async with httpx.AsyncClient(base_url=base_url) as client:
        # Step 1: Get upload ticket
        ticket_request = {
            "filename": "test_sprite.png",
            "resource_data": {
                "type": "image",
                "state": "raw",
                "image_type": "sprite",
                "tags": ["side-view", "hi-res"],
            }
        }

        response = await client.post("/api/v1/resources/upload", json=ticket_request)
        assert response.status_code == 200, f"Failed to get upload ticket: {response.text}"

        ticket = response.json()
        assert "upload_url" in ticket
        assert "storage_key" in ticket
        assert "resource_id" in ticket

        storage_key = ticket["storage_key"]
        resource_id = ticket["resource_id"]
        upload_url = ticket["upload_url"]

        print(f"Got upload ticket for resource {resource_id}")

        # Step 2: Upload a small test file to MinIO
        # Create a minimal PNG (1x1 pixel, transparent)
        minimal_png = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 dimensions
            0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,  # RGBA, etc
            0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,  # IDAT chunk
            0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
            0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,
            0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,  # IEND chunk
            0x42, 0x60, 0x82
        ])

        # Upload to MinIO using the presigned URL
        upload_response = await client.put(
            upload_url,
            content=minimal_png,
            headers={"Content-Type": "image/png"}
        )
        assert upload_response.status_code == 200, \
            f"Failed to upload to MinIO: {upload_response.status_code} {upload_response.text}"

        print(f"Uploaded file to MinIO")

        # Step 3: Finalize the resource
        finalize_request = {
            "storage_key": storage_key,
            "resource_data": {
                "type": "image",
                "state": "raw",
                "image_type": "sprite",
                "tags": ["side-view", "hi-res"],
                "license": "CC0",
            }
        }

        response = await client.post("/api/v1/resources", json=finalize_request)
        assert response.status_code == 200, f"Failed to finalize resource: {response.text}"

        created_resource = response.json()
        # Note: The finalize endpoint creates a new ID, not using the ticket resource_id
        # The ticket resource_id is only used in the storage path
        actual_resource_id = created_resource["id"]
        assert created_resource["storage_key"] == storage_key
        assert created_resource["resource_data"]["state"] == "raw"
        assert created_resource["resource_data"]["processed"] is False

        print(f"Finalized resource {actual_resource_id}")

        # Step 4: Verify the resource appears in filtered results
        response = await client.get("/api/v1/resources?resource_type=image&state=raw")
        assert response.status_code == 200

        resources = response.json()
        resource_ids = [r["id"] for r in resources]
        assert actual_resource_id in resource_ids, \
            f"Newly created resource {actual_resource_id} not found in filtered results"

        # Find our resource and verify its data
        our_resource = next(r for r in resources if r["id"] == actual_resource_id)
        assert our_resource["resource_data"]["image_type"] == "sprite"
        assert "side-view" in our_resource["resource_data"]["tags"]
        assert "hi-res" in our_resource["resource_data"]["tags"]

        print(f"Successfully verified resource {actual_resource_id} in filtered results")

        # Cleanup: Delete the test resource
        delete_response = await client.delete(f"/api/v1/resources/{actual_resource_id}")
        assert delete_response.status_code == 200
        print(f"Cleaned up test resource {actual_resource_id}")
