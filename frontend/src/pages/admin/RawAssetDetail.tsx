import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';

interface AssetData {
  name: string;
  path: string;
  metadata: {
    source_url?: string;
  };
  derived: Array<{
    name: string;
    path: string;
    metadata: any;
  }>;
}

const RawAssetDetail: React.FC = () => {
  const { filename } = useParams<{ filename: string }>();
  const [asset, setAsset] = useState<AssetData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!filename) return;

    // Load raw manifest and grouped manifest
    Promise.all([
      fetch('/assets/art/raw/sprites/manifest.json').then(r => r.json()),
      fetch('/assets/art/grouped/sprites/manifest.json').then(r => r.json())
    ])
      .then(([rawData, groupedData]) => {
        // Find this asset in raw manifest
        const rawAsset = rawData.assets.find((a: any) => a.name === filename);
        if (!rawAsset) throw new Error('Asset not found');

        // Find derived sprites (grouped sprites that came from this raw file)
        const rawFilePath = `assets/art/raw/sprites/${filename}`;
        const derived = groupedData.assets.filter((a: any) =>
          a.metadata.raw_file === rawFilePath
        );

        setAsset({
          name: rawAsset.name,
          path: rawAsset.path,
          metadata: rawAsset.metadata,
          derived: derived
        });
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

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '20px' }}>
        <Link to="/admin/assets/raw" style={{ marginRight: '15px' }}>← Back to Raw Assets</Link>
        <Link to="/admin/assets/grouped">Grouped Assets</Link>
      </div>

      <div style={{ background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', marginBottom: '20px' }}>
        <h1>{asset.name}</h1>
        <div style={{ textAlign: 'center', padding: '20px', background: '#fff', maxHeight: '600px', overflow: 'auto' }}>
          <img src={asset.path} alt={asset.name} style={{ maxWidth: '100%', maxHeight: '500px', imageRendering: 'pixelated', border: '1px solid #ddd' }} />
        </div>
      </div>

      <div style={{ background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', marginBottom: '20px' }}>
        <h2>Metadata</h2>
        <div style={{ fontFamily: 'monospace', textAlign: 'left' }}>
          <p><strong>source_url:</strong> {asset.metadata.source_url ? (
            <a href={asset.metadata.source_url} target="_blank" rel="noopener noreferrer">
              {asset.metadata.source_url}
            </a>
          ) : 'N/A'}</p>
        </div>
      </div>

      <div style={{ background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h2>Derived Sprites ({asset.derived.length})</h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
          {asset.derived.map((sprite) => (
            <div key={sprite.name} style={{ textAlign: 'center' }}>
              <Link to={`/admin/assets/grouped/${sprite.name}`}>
                <img
                  src={sprite.path}
                  alt={sprite.name}
                  title={sprite.name}
                  style={{ maxWidth: '64px', maxHeight: '64px', imageRendering: 'pixelated', border: '1px solid #ddd' }}
                />
                <br />
                <small>{sprite.name}</small>
              </Link>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RawAssetDetail;
