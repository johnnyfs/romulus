"""
Admin interface for viewing and vetting game assets.
Simple HTML pages for browsing raw and grouped assets.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
import yaml
from typing import Dict, List, Optional

router = APIRouter(prefix="/admin/assets", tags=["admin"])

# Base paths
REPO_ROOT = Path(__file__).parent.parent.parent
ASSETS_ROOT = REPO_ROOT / "assets/art"
RAW_SPRITES = ASSETS_ROOT / "raw/sprites"
GROUPED_SPRITES = ASSETS_ROOT / "grouped/sprites"


def load_yaml(path: Path) -> Dict:
    """Load YAML metadata file."""
    if path.exists():
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}


def get_raw_sprites() -> List[Dict]:
    """Get list of raw sprite files with metadata."""
    sprites = []
    for png_file in sorted(RAW_SPRITES.glob("*.png")):
        yaml_file = png_file.with_suffix('.yaml')
        metadata = load_yaml(yaml_file)
        sprites.append({
            'name': png_file.name,
            'path': f"/assets/art/raw/sprites/{png_file.name}",
            'metadata': metadata
        })
    return sprites


def get_grouped_sprites() -> List[Dict]:
    """Get list of grouped sprite files with metadata."""
    sprites = []
    for png_file in sorted(GROUPED_SPRITES.glob("*.png")):
        yaml_file = png_file.with_suffix('.yaml')
        metadata = load_yaml(yaml_file)
        sprites.append({
            'name': png_file.name,
            'path': f"/assets/art/grouped/sprites/{png_file.name}",
            'metadata': metadata
        })
    return sprites


def get_derived_sprites(raw_filename: str) -> List[Dict]:
    """Get all grouped sprites derived from a raw file."""
    raw_path = f"assets/art/raw/sprites/{raw_filename}"
    derived = []

    for png_file in sorted(GROUPED_SPRITES.glob("*.png")):
        yaml_file = png_file.with_suffix('.yaml')
        metadata = load_yaml(yaml_file)

        if metadata.get('raw_file') == raw_path:
            derived.append({
                'name': png_file.name,
                'path': f"/assets/art/grouped/sprites/{png_file.name}",
                'metadata': metadata
            })

    return derived


@router.get("/raw", response_class=HTMLResponse)
async def list_raw_assets():
    """List all raw sprite assets."""
    sprites = get_raw_sprites()

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Raw Assets</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            h1 { color: #333; }
            table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #4CAF50; color: white; }
            tr:hover { background: #f5f5f5; }
            a { color: #2196F3; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .nav { margin-bottom: 20px; }
            .nav a { margin-right: 15px; padding: 8px 16px; background: #2196F3; color: white; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/admin/assets/raw">Raw Assets</a>
            <a href="/admin/assets/grouped">Grouped Assets</a>
        </div>
        <h1>Raw Sprite Assets</h1>
        <table>
            <tr>
                <th>Preview</th>
                <th>Filename</th>
                <th>Source URL</th>
                <th>Actions</th>
            </tr>
    """

    for sprite in sprites:
        source_url = sprite['metadata'].get('source_url', 'N/A')
        source_link = f'<a href="{source_url}" target="_blank">{source_url}</a>' if source_url != 'N/A' else 'N/A'

        html += f"""
            <tr>
                <td><img src="{sprite['path']}" style="max-width: 100px; max-height: 100px; image-rendering: pixelated;"/></td>
                <td>{sprite['name']}</td>
                <td>{source_link}</td>
                <td><a href="/admin/assets/raw/{sprite['name']}">View Details</a></td>
            </tr>
        """

    html += """
        </table>
    </body>
    </html>
    """

    return html


@router.get("/raw/{filename}", response_class=HTMLResponse)
async def view_raw_asset(filename: str):
    """View individual raw asset with metadata and derived sprites."""
    png_file = RAW_SPRITES / filename
    yaml_file = png_file.with_suffix('.yaml')

    if not png_file.exists():
        raise HTTPException(status_code=404, detail="Asset not found")

    metadata = load_yaml(yaml_file)
    derived = get_derived_sprites(filename)

    # Format YAML for display
    yaml_content = yaml.dump(metadata, default_flow_style=False, sort_keys=False) if metadata else "No metadata"

    source_url = metadata.get('source_url', '')
    source_link = f'<a href="{source_url}" target="_blank">{source_url}</a>' if source_url else 'N/A'

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{filename}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            h1, h2 {{ color: #333; }}
            .container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            .image-container {{ text-align: center; padding: 20px; background: #fff; }}
            .image-container img {{ max-width: 100%; image-rendering: pixelated; border: 1px solid #ddd; }}
            pre {{ background: #f4f4f4; padding: 15px; border-radius: 4px; overflow-x: auto; }}
            .derived {{ display: flex; flex-wrap: wrap; gap: 10px; }}
            .derived-item {{ text-align: center; }}
            .derived-item img {{ max-width: 64px; max-height: 64px; image-rendering: pixelated; border: 1px solid #ddd; }}
            .nav {{ margin-bottom: 20px; }}
            .nav a {{ margin-right: 15px; padding: 8px 16px; background: #2196F3; color: white; border-radius: 4px; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/admin/assets/raw">← Back to Raw Assets</a>
            <a href="/admin/assets/grouped">Grouped Assets</a>
        </div>

        <div class="container">
            <h1>{filename}</h1>
            <div class="image-container">
                <img src="/assets/art/raw/sprites/{filename}" />
            </div>
        </div>

        <div class="container">
            <h2>Metadata</h2>
            <p><strong>Source:</strong> {source_link}</p>
            <pre>{yaml_content}</pre>
        </div>

        <div class="container">
            <h2>Derived Sprites ({len(derived)})</h2>
            <div class="derived">
    """

    for derived_sprite in derived:
        html += f"""
                <div class="derived-item">
                    <a href="/admin/assets/grouped/{derived_sprite['name']}">
                        <img src="{derived_sprite['path']}" title="{derived_sprite['name']}" />
                        <br/><small>{derived_sprite['name']}</small>
                    </a>
                </div>
        """

    html += """
            </div>
        </div>
    </body>
    </html>
    """

    return html


@router.get("/grouped", response_class=HTMLResponse)
async def list_grouped_assets():
    """List all grouped sprite assets."""
    sprites = get_grouped_sprites()

    # Group by prefix for better organization
    grouped_by_prefix = {}
    for sprite in sprites:
        prefix = sprite['name'].split('_')[0]
        if prefix not in grouped_by_prefix:
            grouped_by_prefix[prefix] = []
        grouped_by_prefix[prefix].append(sprite)

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Grouped Assets</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            h1, h2 { color: #333; }
            .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
            .sprite-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 10px; }
            .sprite-item { text-align: center; padding: 10px; border: 1px solid #ddd; border-radius: 4px; background: #fafafa; }
            .sprite-item:hover { background: #e3f2fd; }
            .sprite-item img { max-width: 64px; max-height: 64px; image-rendering: pixelated; }
            .sprite-item a { text-decoration: none; color: #333; }
            .nav { margin-bottom: 20px; }
            .nav a { margin-right: 15px; padding: 8px 16px; background: #2196F3; color: white; border-radius: 4px; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/admin/assets/raw">Raw Assets</a>
            <a href="/admin/assets/grouped">Grouped Assets</a>
        </div>
        <h1>Grouped Sprite Assets</h1>
        <p>Total: """ + str(len(sprites)) + """ sprites</p>
    """

    for prefix, prefix_sprites in sorted(grouped_by_prefix.items()):
        html += f"""
        <div class="container">
            <h2>{prefix} ({len(prefix_sprites)} sprites)</h2>
            <div class="sprite-grid">
        """

        for sprite in prefix_sprites[:50]:  # Limit to first 50 per group
            html += f"""
                <div class="sprite-item">
                    <a href="/admin/assets/grouped/{sprite['name']}">
                        <img src="{sprite['path']}" title="{sprite['name']}" />
                        <br/><small>{sprite['name']}</small>
                    </a>
                </div>
            """

        if len(prefix_sprites) > 50:
            html += f"<p><em>... and {len(prefix_sprites) - 50} more</em></p>"

        html += """
            </div>
        </div>
        """

    html += """
    </body>
    </html>
    """

    return html


@router.get("/grouped/{filename}", response_class=HTMLResponse)
async def view_grouped_asset(filename: str):
    """View individual grouped asset with metadata."""
    png_file = GROUPED_SPRITES / filename
    yaml_file = png_file.with_suffix('.yaml')

    if not png_file.exists():
        raise HTTPException(status_code=404, detail="Asset not found")

    metadata = load_yaml(yaml_file)

    # Format YAML for display
    yaml_content = yaml.dump(metadata, default_flow_style=False, sort_keys=False) if metadata else "No metadata"

    source_url = metadata.get('source_url', '')
    source_link = f'<a href="{source_url}" target="_blank">{source_url}</a>' if source_url else 'N/A'

    raw_file = metadata.get('raw_file', '')
    raw_filename = Path(raw_file).name if raw_file else ''
    raw_link = f'<a href="/admin/assets/raw/{raw_filename}">{raw_filename}</a>' if raw_filename else 'N/A'

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{filename}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            h1, h2 {{ color: #333; }}
            .container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            .image-container {{ text-align: center; padding: 40px; background: #fff; }}
            .image-container img {{ image-rendering: pixelated; border: 1px solid #ddd; transform: scale(4); }}
            pre {{ background: #f4f4f4; padding: 15px; border-radius: 4px; overflow-x: auto; }}
            .info {{ display: grid; grid-template-columns: 150px 1fr; gap: 10px; margin-bottom: 15px; }}
            .info dt {{ font-weight: bold; }}
            .nav {{ margin-bottom: 20px; }}
            .nav a {{ margin-right: 15px; padding: 8px 16px; background: #2196F3; color: white; border-radius: 4px; text-decoration: none; }}
            .tags {{ display: flex; flex-wrap: wrap; gap: 5px; }}
            .tag {{ background: #e3f2fd; padding: 4px 8px; border-radius: 4px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/admin/assets/grouped">← Back to Grouped Assets</a>
            <a href="/admin/assets/raw">Raw Assets</a>
        </div>

        <div class="container">
            <h1>{filename}</h1>
            <div class="image-container">
                <img src="/assets/art/grouped/sprites/{filename}" />
            </div>
        </div>

        <div class="container">
            <h2>Metadata</h2>
            <div class="info">
                <dt>Source:</dt>
                <dd>{source_link}</dd>

                <dt>Raw File:</dt>
                <dd>{raw_link}</dd>

                <dt>POV:</dt>
                <dd>{metadata.get('pov', 'N/A')}</dd>

                <dt>Outlined:</dt>
                <dd>{metadata.get('outlined', 'N/A')}</dd>

                <dt>Gender:</dt>
                <dd>{metadata.get('gender', 'N/A')}</dd>

                <dt>Genres:</dt>
                <dd><div class="tags">{"".join(f'<span class="tag">{g}</span>' for g in metadata.get('genres', []))}</div></dd>

                <dt>Tags:</dt>
                <dd><div class="tags">{"".join(f'<span class="tag">{t}</span>' for t in metadata.get('tags', []))}</div></dd>
            </div>

            <h3>Full YAML</h3>
            <pre>{yaml_content}</pre>
        </div>
    </body>
    </html>
    """

    return html
