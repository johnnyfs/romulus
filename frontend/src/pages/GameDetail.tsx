import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import './GameDetail.css';
import { GamesService } from '../client/services/GamesService';
import type { GameGetResponse } from '../client/models/GameGetResponse';
import Chat from '../components/Chat';
import RomPlayer from '../components/RomPlayer';
import ComponentDisplay from '../components/ComponentDisplay';

function GameDetail() {
  const { id } = useParams<{ id: string }>();
  const [game, setGame] = useState<GameGetResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [romData, setRomData] = useState<Uint8Array | null>(null);
  const [romLoading, setRomLoading] = useState(false);

  useEffect(() => {
    const fetchGame = async () => {
      if (!id) return;

      try {
        const response = await GamesService.getGameApiV1GamesGameIdGet(id);
        setGame(response);
        setLoading(false);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch game');
        setLoading(false);
      }
    };

    fetchGame();
  }, [id]);

  // Render ROM from game data
  useEffect(() => {
    const renderRom = async () => {
      if (!id) return;

      try {
        setRomLoading(true);
        console.log('Rendering ROM for game:', id);

        // Call the render endpoint directly with fetch (can't use generated client for binary data)
        const response = await fetch(`http://localhost:8000/api/v1/games/${id}/render`, {
          method: 'POST',
        });

        if (!response.ok) {
          throw new Error(`Failed to render ROM: ${response.status} ${response.statusText}`);
        }

        // The response is binary, convert it to Uint8Array
        const arrayBuffer = await response.arrayBuffer();
        const romBytes = new Uint8Array(arrayBuffer);

        // Check for NES header magic bytes
        const header = String.fromCharCode(...romBytes.slice(0, 4));
        console.log('ROM header:', header, 'Length:', romBytes.length);

        if (!header.startsWith('NES')) {
          console.error('Invalid NES ROM - first bytes:', Array.from(romBytes.slice(0, 16)));
          throw new Error('Invalid NES ROM format');
        }

        console.log('✅ ROM rendered successfully:', romBytes.length, 'bytes');
        setRomData(romBytes);
        setRomLoading(false);
      } catch (err: any) {
        console.error('Failed to render ROM:', err);
        setError(err.message || 'Failed to render ROM');
        setRomLoading(false);
      }
    };

    renderRom();
  }, [id]);

  if (loading) {
    return (
      <div className="game-detail-loading">
        <h2>Loading...</h2>
      </div>
    );
  }

  if (error) {
    return (
      <div className="game-detail-error">
        <h2 className="game-detail-error-title">Error</h2>
        <p>{error}</p>
        <Link to="/">Back to Home</Link>
      </div>
    );
  }

  return (
    <div className="game-detail-container">
      {/* Header */}
      <div className="game-detail-header">
        <Link to="/" className="game-detail-back-link">← Back</Link>
        <h2 className="game-detail-title">{game?.name}</h2>
      </div>

      {/* Three Column Layout */}
      <div className="game-detail-layout">
        {/* Left Column - Chat */}
        <div className="game-detail-column">
          <Chat gameId={id || ''} />
        </div>

        {/* Middle Column - ROM Player */}
        <div className="game-detail-column">
          {romLoading ? (
            <div className="game-detail-rom-loading">
              <h3>Rendering ROM...</h3>
              <p className="game-detail-rom-loading-subtitle">Building your NES game</p>
            </div>
          ) : (
            <RomPlayer gameId={id || ''} romData={romData} />
          )}
        </div>

        {/* Right Column - Component Display */}
        <div className="game-detail-column">
          <ComponentDisplay game={game} />
        </div>
      </div>
    </div>
  );
}

export default GameDetail;
