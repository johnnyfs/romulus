import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import styles from './GameDetail.module.css';
import { GamesService } from '../client/services/GamesService';
import type { GameGetResponse } from '../client/models/GameGetResponse';
import { OpenAPI } from '../client/core/OpenAPI';
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

  const fetchGame = async () => {
    if (!id) return;

    try {
      const response = await GamesService.getGameGamesGameIdGet(id);
      setGame(response);
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch game');
      setLoading(false);
    }
  };

  const renderRom = async () => {
    if (!id) return;

    try {
      setRomLoading(true);
      console.log('Rendering ROM for game:', id);

      // Call the render endpoint directly with fetch (can't use generated client for binary data)
      // The generated client's getResponseBody() always converts to JSON/text, which corrupts binary data
      // We use OpenAPI.BASE (which includes /api/v1) to respect port configuration
      const response = await fetch(`${OpenAPI.BASE}/games/${id}/render`, {
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

  const handleRebuildROM = () => {
    renderRom();
  };

  const handleSceneUpdated = () => {
    fetchGame();
  };

  useEffect(() => {
    fetchGame();
  }, [id]);

  // Render ROM from game data
  useEffect(() => {
    renderRom();
  }, [id]);

  if (loading) {
    return (
      <div className={styles.gameDetailLoading}>
        <h2>Loading...</h2>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.gameDetailError}>
        <h2 className={styles.gameDetailErrorTitle}>Error</h2>
        <p>{error}</p>
        <Link to="/">Back to Home</Link>
      </div>
    );
  }

  return (
    <div className={styles.gameDetailContainer}>
      {/* Header */}
      <div className={styles.gameDetailHeader}>
        <Link to="/" className={styles.gameDetailBackLink}>← Back</Link>
        <h2 className={styles.gameDetailTitle}>{game?.name}</h2>
      </div>

      {/* Three Column Layout */}
      <div className={styles.gameDetailLayout}>
        {/* Left Column - Chat */}
        <div className={styles.gameDetailColumn}>
          <Chat gameId={id || ''} />
        </div>

        {/* Middle Column - ROM Player */}
        <div className={styles.gameDetailColumn}>
          {romLoading ? (
            <div className={styles.gameDetailRomLoading}>
              <h3>Rendering ROM...</h3>
              <p className={styles.gameDetailRomLoadingSubtitle}>Building your NES game</p>
            </div>
          ) : (
            <RomPlayer gameId={id || ''} romData={romData} />
          )}
        </div>

        {/* Right Column - Component Display */}
        <div className={styles.gameDetailColumn}>
          <ComponentDisplay
            game={game}
            onRebuildROM={handleRebuildROM}
            onSceneUpdated={handleSceneUpdated}
          />
        </div>
      </div>
    </div>
  );
}

export default GameDetail;
