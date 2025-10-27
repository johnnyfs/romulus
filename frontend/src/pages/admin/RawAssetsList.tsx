import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

interface RawAsset {
  name: string;
  path: string;
  metadata: {
    source_url?: string;
  };
}

const RawAssetsList: React.FC = () => {
  const [assets, setAssets] = useState<RawAsset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/assets/art/raw/sprites/manifest.json')
      .then((response) => response.json())
      .then((data) => {
        setAssets(data.assets);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '20px' }}>
        <Link to="/" style={{ marginRight: '15px' }}>← Home</Link>
        <Link to="/admin/assets/raw" style={{ marginRight: '15px', fontWeight: 'bold' }}>Raw Assets</Link>
        <Link to="/admin/assets/grouped">Grouped Assets</Link>
      </div>

      <h1>Raw Sprite Assets</h1>

      {loading && <p>Loading assets...</p>}

      {error && (
        <div style={{ color: 'red', padding: '10px', border: '1px solid red', borderRadius: '4px', backgroundColor: '#fee' }}>
          Error: {error}
        </div>
      )}

      {!loading && !error && (
        <table style={{ width: '100%', borderCollapse: 'collapse', background: 'white', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <thead>
            <tr style={{ background: '#4CAF50', color: 'white' }}>
              <th style={{ padding: '12px', textAlign: 'left' }}>Preview</th>
              <th style={{ padding: '12px', textAlign: 'left' }}>Filename</th>
              <th style={{ padding: '12px', textAlign: 'left' }}>Source URL</th>
              <th style={{ padding: '12px', textAlign: 'left' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {assets.map((asset) => (
              <tr key={asset.name} style={{ borderBottom: '1px solid #ddd' }}>
                <td style={{ padding: '12px' }}>
                  <img
                    src={asset.path}
                    alt={asset.name}
                    style={{ maxWidth: '100px', maxHeight: '100px', imageRendering: 'pixelated' }}
                  />
                </td>
                <td style={{ padding: '12px' }}>{asset.name}</td>
                <td style={{ padding: '12px' }}>
                  {asset.metadata.source_url ? (
                    <a href={asset.metadata.source_url} target="_blank" rel="noopener noreferrer">
                      {asset.metadata.source_url}
                    </a>
                  ) : (
                    'N/A'
                  )}
                </td>
                <td style={{ padding: '12px' }}>
                  <Link to={`/admin/assets/raw/${asset.name}`}>View Details</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default RawAssetsList;
