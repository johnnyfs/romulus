import React from 'react';
import type { GameGetResponse } from '../client/models/GameGetResponse';

interface ComponentDisplayProps {
  game: GameGetResponse | null;
}

function ComponentDisplay({ game }: ComponentDisplayProps) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      border: '1px solid #ddd',
      borderRadius: '4px',
      backgroundColor: '#fff'
    }}>
      <div style={{
        padding: '10px',
        borderBottom: '1px solid #ddd',
        backgroundColor: '#f5f5f5',
        fontWeight: 'bold'
      }}>
        Component Inspector
      </div>

      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '15px'
      }}>
        {!game ? (
          <div style={{ color: '#999', textAlign: 'center', marginTop: '20px' }}>
            Loading game data...
          </div>
        ) : (
          <div>
            <h3 style={{ marginTop: 0 }}>Game: {game.name}</h3>

            <div style={{ marginBottom: '20px' }}>
              <strong>ID:</strong> <code>{game.id}</code>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <h4>Scenes ({game.scenes.length})</h4>
              {game.scenes.length === 0 ? (
                <p style={{ color: '#999' }}>No scenes yet</p>
              ) : (
                <ul style={{ listStyle: 'none', padding: 0 }}>
                  {game.scenes.map((scene) => (
                    <li key={scene.id} style={{
                      padding: '10px',
                      marginBottom: '8px',
                      border: '1px solid #e0e0e0',
                      borderRadius: '4px',
                      backgroundColor: '#f9f9f9'
                    }}>
                      <div style={{ fontWeight: 'bold' }}>{scene.name}</div>
                      <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                        ID: {scene.id}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <details style={{ marginTop: '20px' }}>
              <summary style={{ cursor: 'pointer', fontWeight: 'bold', marginBottom: '10px' }}>
                Raw Data
              </summary>
              <pre style={{
                backgroundColor: '#f5f5f5',
                padding: '10px',
                borderRadius: '4px',
                fontSize: '12px',
                overflow: 'auto',
                border: '1px solid #ddd'
              }}>
                {JSON.stringify(game, null, 2)}
              </pre>
            </details>
          </div>
        )}
      </div>
    </div>
  );
}

export default ComponentDisplay;
