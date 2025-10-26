import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
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
    <div style={{ padding: '20px', maxWidth: '500px', margin: '0 auto' }}>
      <h1>Create New Game</h1>

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="gameName" style={{ display: 'block', marginBottom: '5px' }}>
            Game Name:
          </label>
          <input
            id="gameName"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '8px',
              fontSize: '16px',
              border: '1px solid #ccc',
              borderRadius: '4px'
            }}
            disabled={loading}
          />
        </div>

        {error && (
          <div style={{
            color: 'red',
            marginBottom: '15px',
            padding: '10px',
            border: '1px solid red',
            borderRadius: '4px',
            backgroundColor: '#fee'
          }}>
            Error: {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !name.trim()}
          style={{
            padding: '10px 20px',
            fontSize: '16px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading || !name.trim() ? 'not-allowed' : 'pointer',
            opacity: loading || !name.trim() ? 0.6 : 1
          }}
        >
          {loading ? 'Creating...' : 'Create Game'}
        </button>
      </form>
    </div>
  );
}

export default CreateGame;
