import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './CreateGame.module.css';
import { GamesService } from '../client/services/GamesService';

function CreateGame() {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await GamesService.createGameApiV1GamesPost(
        { name: name },
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
