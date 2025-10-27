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
        <div style={{ textAlign: 'center', padding: '40px', background: '#fff' }}>
          <img
            src={asset.path}
            alt={asset.name}
            style={{ imageRendering: 'pixelated', border: '1px solid #ddd', transform: 'scale(4)' }}
          />
        </div>
      </div>

      <div style={{ background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h2>Metadata</h2>
        <div style={{ display: 'grid', gridTemplateColumns: '150px 1fr', gap: '10px', marginBottom: '15px' }}>
          <dt style={{ fontWeight: 'bold' }}>Source:</dt>
          <dd>
            {asset.metadata.source_url ? (
              <a href={asset.metadata.source_url} target="_blank" rel="noopener noreferrer">
                {asset.metadata.source_url}
              </a>
            ) : (
              'N/A'
            )}
          </dd>

          <dt style={{ fontWeight: 'bold' }}>Raw File:</dt>
          <dd>
            {rawFilename ? (
              <Link to={`/admin/assets/raw/${rawFilename}`}>{rawFilename}</Link>
            ) : (
              'N/A'
            )}
          </dd>

          <dt style={{ fontWeight: 'bold' }}>POV:</dt>
          <dd>{asset.metadata.pov || 'N/A'}</dd>

          <dt style={{ fontWeight: 'bold' }}>Outlined:</dt>
          <dd>{asset.metadata.outlined !== undefined ? String(asset.metadata.outlined) : 'N/A'}</dd>

          <dt style={{ fontWeight: 'bold' }}>Gender:</dt>
          <dd>{asset.metadata.gender || 'N/A'}</dd>

          <dt style={{ fontWeight: 'bold' }}>Genres:</dt>
          <dd>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
              {asset.metadata.genres?.map((genre) => (
                <span key={genre} style={{ background: '#e3f2fd', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>
                  {genre}
                </span>
              ))}
            </div>
          </dd>

          <dt style={{ fontWeight: 'bold' }}>Tags:</dt>
          <dd>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
              {asset.metadata.tags?.map((tag) => (
                <span key={tag} style={{ background: '#e3f2fd', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>
                  {tag}
                </span>
              ))}
            </div>
          </dd>
        </div>

        <h3>Full YAML</h3>
        <pre style={{ background: '#f4f4f4', padding: '15px', borderRadius: '4px', overflowX: 'auto' }}>
          {JSON.stringify(asset.metadata, null, 2)}
        </pre>
      </div>
    </div>
  );
};

export default GroupedAssetDetail;
