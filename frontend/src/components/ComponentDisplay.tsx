import React from 'react';
import styles from './ComponentDisplay.module.css';
import type { GameGetResponse } from '../client/models/GameGetResponse';

interface ComponentDisplayProps {
  game: GameGetResponse | null;
}

function ComponentDisplay({ game }: ComponentDisplayProps) {
  return (
    <div className={styles.componentDisplayContainer}>
      <div className={styles.componentDisplayHeader}>
        Component Inspector
      </div>

      <div className={styles.componentDisplayContent}>
        {!game ? (
          <div className={styles.componentDisplayLoading}>
            Loading game data...
          </div>
        ) : (
          <div>
            <h3 className={styles.componentDisplayGameTitle}>Game: {game.name}</h3>

            <div className={styles.componentDisplayGameId}>
              <strong>ID:</strong> <code>{game.id}</code>
            </div>

            <div className={styles.componentDisplaySection}>
              <h4 className={styles.componentDisplaySectionTitle}>Scenes ({game.scenes.length})</h4>
              {game.scenes.length === 0 ? (
                <p className={styles.componentDisplayEmpty}>No scenes yet</p>
              ) : (
                <ul className={styles.componentDisplayScenesList}>
                  {game.scenes.map((scene) => (
                    <li key={scene.id} className={styles.componentDisplaySceneItem}>
                      <div className={styles.componentDisplaySceneName}>{scene.name}</div>
                      <div className={styles.componentDisplaySceneId}>
                        ID: {scene.id}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <details className={styles.componentDisplayDetails}>
              <summary className={styles.componentDisplayDetailsSummary}>
                Raw Data
              </summary>
              <pre className={styles.componentDisplayDetailsPre}>
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
