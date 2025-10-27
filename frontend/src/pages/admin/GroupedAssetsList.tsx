import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

interface GroupedAsset {
  name: string;
  path: string;
  metadata: any;
}

interface GroupedData {
  assets: GroupedAsset[];
  grouped: Record<string, GroupedAsset[]>;
}

const GroupedAssetsList: React.FC = () => {
  const [data, setData] = useState<GroupedData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/assets/art/grouped/sprites/manifest.json')
      .then((response) => response.json())
      .then((responseData) => {
        setData(responseData);
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
        <Link to="/admin/assets/raw" style={{ marginRight: '15px' }}>Raw Assets</Link>
        <Link to="/admin/assets/grouped" style={{ fontWeight: 'bold' }}>Grouped Assets</Link>
      </div>

      <h1>Grouped Sprite Assets</h1>
      {data && <p>Total: {data.assets.length} sprites</p>}

      {loading && <p>Loading assets...</p>}

      {error && (
        <div style={{ color: 'red', padding: '10px', border: '1px solid red', borderRadius: '4px', backgroundColor: '#fee' }}>
          Error: {error}
        </div>
      )}

      {!loading && !error && data && (
        <>
          {Object.entries(data.grouped).map(([prefix, sprites]) => (
            <div key={prefix} style={{ background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', marginBottom: '20px' }}>
              <h2>{prefix} ({sprites.length} sprites)</h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))', gap: '10px' }}>
                {sprites.slice(0, 50).map((sprite) => (
                  <div
                    key={sprite.name}
                    style={{ textAlign: 'center', padding: '10px', border: '1px solid #ddd', borderRadius: '4px', background: '#fafafa' }}
                  >
                    <Link to={`/admin/assets/grouped/${sprite.name}`} style={{ textDecoration: 'none', color: '#333' }}>
                      <img
                        src={sprite.path}
                        alt={sprite.name}
                        title={sprite.name}
                        style={{ maxWidth: '64px', maxHeight: '64px', imageRendering: 'pixelated' }}
                      />
                      <br />
                      <small>{sprite.name}</small>
                    </Link>
                  </div>
                ))}
              </div>
              {sprites.length > 50 && <p><em>... and {sprites.length - 50} more</em></p>}
            </div>
          ))}
        </>
      )}
    </div>
  );
};

export default GroupedAssetsList;
