import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';

interface AssetData {
  name: string;
  path: string;
  metadata: {
    source_url?: string;
    raw_file?: string;
    source_rect?: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
    pov?: string;
    outlined?: boolean;
    genres?: string[];
    gender?: string;
    tags?: string[];
  };
}

const GroupedAssetDetail: React.FC = () => {
  const { filename } = useParams<{ filename: string }>();
  const [asset, setAsset] = useState<AssetData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!filename) return;

    fetch('/assets/art/grouped/sprites/manifest.json')
      .then((response) => response.json())
      .then((data) => {
        // Find this asset in the manifest
        const foundAsset = data.assets.find((a: any) => a.name === filename);
        if (!foundAsset) throw new Error('Asset not found');

        setAsset(foundAsset);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [filename]);

  if (loading) return <div style={{ padding: '20px' }}>Loading...</div>;
  if (error) return <div style={{ padding: '20px', color: 'red' }}>Error: {error}</div>;
  if (!asset) return <div style={{ padding: '20px' }}>Asset not found</div>;

  const rawFilename = asset.metadata.raw_file ? asset.metadata.raw_file.split('/').pop() : '';

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '20px' }}>
        <Link to="/admin/assets/grouped" style={{ marginRight: '15px' }}>← Back to Grouped Assets</Link>
        <Link to="/admin/assets/raw">Raw Assets</Link>
      </div>

      <div style={{ background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', marginBottom: '20px' }}>
        <h1>{asset.name}</h1>
        <div style={{ textAlign: 'center', padding: '40px', background: '#fff', maxHeight: '600px', overflow: 'auto' }}>
          <img
            src={asset.path}
            alt={asset.name}
            style={{ imageRendering: 'pixelated', border: '1px solid #ddd', maxWidth: '100%', maxHeight: '500px' }}
          />
        </div>
      </div>

      <div style={{ background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h2>Metadata</h2>
        <div style={{ fontFamily: 'monospace', textAlign: 'left' }}>
          <p><strong>source_url:</strong> {asset.metadata.source_url ? (
            <a href={asset.metadata.source_url} target="_blank" rel="noopener noreferrer">
              {asset.metadata.source_url}
            </a>
          ) : 'N/A'}</p>

          <p><strong>raw_file:</strong> {rawFilename ? (
            <Link to={`/admin/assets/raw/${rawFilename}`}>{rawFilename}</Link>
          ) : 'N/A'}</p>

          <p><strong>source_rect:</strong></p>
          <div style={{ marginLeft: '20px' }}>
            <p>x: {asset.metadata.source_rect?.x || 0}</p>
            <p>y: {asset.metadata.source_rect?.y || 0}</p>
            <p>width: {asset.metadata.source_rect?.width || 0}</p>
            <p>height: {asset.metadata.source_rect?.height || 0}</p>
          </div>

          <p><strong>pov:</strong> {asset.metadata.pov || 'N/A'}</p>

          <p><strong>outlined:</strong> {asset.metadata.outlined !== undefined ? String(asset.metadata.outlined) : 'N/A'}</p>

          <p><strong>genres:</strong></p>
          {asset.metadata.genres && asset.metadata.genres.length > 0 ? (
            <div style={{ marginLeft: '20px' }}>
              {asset.metadata.genres.map((genre: string) => (
                <p key={genre}>- {genre}</p>
              ))}
            </div>
          ) : (
            <p style={{ marginLeft: '20px' }}>[]</p>
          )}

          <p><strong>gender:</strong> {asset.metadata.gender || 'N/A'}</p>

          <p><strong>tags:</strong></p>
          {asset.metadata.tags && asset.metadata.tags.length > 0 ? (
            <div style={{ marginLeft: '20px' }}>
              {asset.metadata.tags.map((tag: string) => (
                <p key={tag}>- {tag}</p>
              ))}
            </div>
          ) : (
            <p style={{ marginLeft: '20px' }}>[]</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default GroupedAssetDetail;
