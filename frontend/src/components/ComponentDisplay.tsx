import React from 'react';
import './ComponentDisplay.css';
import type { GameGetResponse } from '../client/models/GameGetResponse';

interface ComponentDisplayProps {
  game: GameGetResponse | null;
}

function ComponentDisplay({ game }: ComponentDisplayProps) {
  return (
    <div className="component-display-container">
      <div className="component-display-header">
        Component Inspector
      </div>

      <div className="component-display-content">
        {!game ? (
          <div className="component-display-loading">
            Loading game data...
          </div>
        ) : (
          <div>
            <h3 className="component-display-game-title">Game: {game.name}</h3>

            <div className="component-display-game-id">
              <strong>ID:</strong> <code>{game.id}</code>
            </div>

            <div className="component-display-section">
              <h4 className="component-display-section-title">Scenes ({game.scenes.length})</h4>
              {game.scenes.length === 0 ? (
                <p className="component-display-empty">No scenes yet</p>
              ) : (
                <ul className="component-display-scenes-list">
                  {game.scenes.map((scene) => (
                    <li key={scene.id} className="component-display-scene-item">
                      <div className="component-display-scene-name">{scene.name}</div>
                      <div className="component-display-scene-id">
                        ID: {scene.id}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <details className="component-display-details">
              <summary className="component-display-details-summary">
                Raw Data
              </summary>
              <pre className="component-display-details-pre">
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
