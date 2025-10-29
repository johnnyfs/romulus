#!/usr/bin/env python3
"""Test the complete asset upload workflow."""

from pathlib import Path

import requests

# Configuration
API_BASE = "http://localhost:8000/api/v1"
ASSET_PATH = Path("/home/johnnyfs/Projects/romulus/assets/art/raw/sprites/popota_people.png")
SOURCE_URL = "https://opengameart.org/content/tricolor-nes-rpg-character-sprite-sheets"

def test_workflow():
    print("=" * 60)
    print("Testing Asset Upload Workflow")
    print("=" * 60)

    # Step 1: Get upload ticket
    print("\n[Step 1] Requesting upload ticket...")
    ticket_response = requests.post(
        f"{API_BASE}/assets/upload",
        json={"filename": ASSET_PATH.name}
    )
    ticket_response.raise_for_status()
    ticket = ticket_response.json()

    print("✓ Got upload ticket")
    print(f"  - Storage key: {ticket['storage_key']}")
    print(f"  - Upload URL: {ticket['upload_url'][:80]}...")

    # Step 2: Upload file to presigned URL
    print(f"\n[Step 2] Uploading file ({ASSET_PATH.stat().st_size} bytes)...")
    with open(ASSET_PATH, "rb") as f:
        file_data = f.read()
        upload_response = requests.put(
            ticket["upload_url"],
            data=file_data,
            headers={"Content-Type": "image/png"}
        )
        upload_response.raise_for_status()

    print("✓ File uploaded successfully")

    # Step 3: Finalize asset with metadata
    print("\n[Step 3] Finalizing asset with metadata...")
    asset_response = requests.post(
        f"{API_BASE}/assets",
        json={
            "storage_key": ticket["storage_key"],
            "asset_data": {
                "type": "image",
                "state": "raw",
                "image_type": "sprite",
                "tags": ["fantasy", "overhead"],
                "source_url": SOURCE_URL,
                "license": "CC-BY 4.0"
            }
        }
    )
    asset_response.raise_for_status()
    asset = asset_response.json()

    print("✓ Asset created")
    print(f"  - Asset ID: {asset['id']}")
    print(f"  - Storage key: {asset['storage_key']}")
    print(f"  - Type: {asset['asset_data']['image_type']}")
    print(f"  - Tags: {', '.join(asset['asset_data']['tags'])}")
    print(f"  - Source: {asset['asset_data']['source_url']}")
    print(f"  - Download URL: {asset['download_url'][:80]}...")

    # Step 4: Retrieve asset by ID
    print("\n[Step 4] Retrieving asset by ID...")
    get_response = requests.get(f"{API_BASE}/assets/{asset['id']}")
    get_response.raise_for_status()
    retrieved_asset = get_response.json()

    print("✓ Asset retrieved")
    print(f"  - Matches created asset: {retrieved_asset['id'] == asset['id']}")
    print(f"  - Has download URL: {bool(retrieved_asset.get('download_url'))}")

    # Step 5: Download the file using the download URL
    print("\n[Step 5] Testing download URL...")
    download_response = requests.get(retrieved_asset['download_url'])
    download_response.raise_for_status()
    downloaded_data = download_response.content

    print("✓ File downloaded")
    print(f"  - Downloaded size: {len(downloaded_data)} bytes")
    print(f"  - Original size: {len(file_data)} bytes")
    print(f"  - Data matches: {downloaded_data == file_data}")

    # Step 6: Clean up - delete the asset
    print("\n[Step 6] Cleaning up - deleting asset...")
    delete_response = requests.delete(f"{API_BASE}/assets/{asset['id']}")
    delete_response.raise_for_status()

    print("✓ Asset deleted")

    # Verify deletion
    verify_response = requests.get(f"{API_BASE}/assets/{asset['id']}")
    print(f"  - Verify deletion: {verify_response.status_code == 404}")

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_workflow()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
