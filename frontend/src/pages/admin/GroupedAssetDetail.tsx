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
        <p>
          <strong>Source:</strong>{' '}
          {asset.metadata.source_url ? (
            <a href={asset.metadata.source_url} target="_blank" rel="noopener noreferrer">
              {asset.metadata.source_url}
            </a>
          ) : (
            'N/A'
          )}
        </p>
        <p>
          <strong>Raw File:</strong>{' '}
          {rawFilename ? (
            <Link to={`/admin/assets/raw/${rawFilename}`}>{rawFilename}</Link>
          ) : (
            'N/A'
          )}
        </p>
        <pre style={{ background: '#f4f4f4', padding: '15px', borderRadius: '4px', overflowX: 'auto', whiteSpace: 'pre' }}>
          {JSON.stringify(asset.metadata, null, 0)}
        </pre>
      </div>
    </div>
  );
};

export default GroupedAssetDetail;
