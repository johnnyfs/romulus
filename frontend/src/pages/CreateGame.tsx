import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './CreateGame.module.css';
import { GamesService } from '../client/services/GamesService';
import { NESSpriteSize } from '../client/models/NESSpriteSize';

function CreateGame() {
  const [name, setName] = useState('');
  const [spriteSize, setSpriteSize] = useState<NESSpriteSize>(NESSpriteSize._8X8);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await GamesService.createGameGamesPost(
        {
          name: name,
          game_data: {
            type: 'nes',
            sprite_size: spriteSize
          }
        },
        true  // default_ = true to create with default scene
      );

      // Redirect to the game detail page
      navigate(`/games/${response.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to create game');
      setLoading(false);
    }
  };

  return (
    <div className={styles.createGameContainer}>
      <h1 className={styles.createGameTitle}>Create New Game</h1>

      <form onSubmit={handleSubmit} className={styles.createGameForm}>
        <div className={styles.createGameFormGroup}>
          <label htmlFor="gameName" className={styles.createGameLabel}>
            Game Name:
          </label>
          <input
            id="gameName"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className={styles.createGameInput}
            disabled={loading}
          />
        </div>

        <div className={styles.createGameFormGroup}>
          <label htmlFor="spriteSize" className={styles.createGameLabel}>
            Sprite Style:
          </label>
          <select
            id="spriteSize"
            value={spriteSize}
            onChange={(e) => setSpriteSize(e.target.value as NESSpriteSize)}
            className={styles.createGameInput}
            disabled={loading}
          >
            <option value={NESSpriteSize._8X8}>Arcade (8x8)</option>
            <option value={NESSpriteSize._8X16}>Console (8x16)</option>
          </select>
        </div>

        {error && (
          <div className={styles.createGameError}>
            Error: {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !name.trim()}
          className={styles.createGameSubmitButton}
        >
          {loading ? 'Creating...' : 'Create Game'}
        </button>
      </form>
    </div>
  );
}

export default CreateGame;
