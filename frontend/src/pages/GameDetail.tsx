import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
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

  // Load test ROM
  useEffect(() => {
    const loadRom = async () => {
      try {
        const response = await fetch('/test.nes');
        console.log('ROM fetch response:', response.status, response.headers.get('content-type'));

        if (!response.ok) {
          throw new Error(`Failed to fetch ROM: ${response.status} ${response.statusText}`);
        }

        const arrayBuffer = await response.arrayBuffer();
        const romBytes = new Uint8Array(arrayBuffer);

        // Check for NES header magic bytes
        const header = String.fromCharCode(...romBytes.slice(0, 4));
        console.log('ROM header:', header, 'Length:', romBytes.length);

        if (!header.startsWith('NES')) {
          console.error('Invalid NES ROM - first bytes:', Array.from(romBytes.slice(0, 16)));
          throw new Error('Invalid NES ROM format');
        }

        setRomData(romBytes);
      } catch (err: any) {
        console.error('Failed to load ROM:', err);
        setError(err.message || 'Failed to load ROM');
      }
    };

    loadRom();
  }, []);

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h2>Loading...</h2>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px' }}>
        <h2 style={{ color: 'red' }}>Error</h2>
        <p>{error}</p>
        <Link to="/">Back to Home</Link>
      </div>
    );
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{
        padding: '10px 20px',
        borderBottom: '1px solid #ddd',
        backgroundColor: '#f5f5f5',
        display: 'flex',
        alignItems: 'center',
        gap: '20px'
      }}>
        <Link to="/" style={{ textDecoration: 'none', color: '#007bff' }}>← Back</Link>
        <h2 style={{ margin: 0 }}>{game?.name}</h2>
      </div>

      {/* Three Column Layout */}
      <div style={{
        flex: 1,
        display: 'grid',
        gridTemplateColumns: '300px 1fr 350px',
        gap: '10px',
        padding: '10px',
        overflow: 'hidden'
      }}>
        {/* Left Column - Chat */}
        <div style={{ overflow: 'hidden' }}>
          <Chat gameId={id || ''} />
        </div>

        {/* Middle Column - ROM Player */}
        <div style={{ overflow: 'hidden' }}>
          <RomPlayer gameId={id || ''} romData={romData} />
        </div>

        {/* Right Column - Component Display */}
        <div style={{ overflow: 'hidden' }}>
          <ComponentDisplay game={game} />
        </div>
      </div>
    </div>
  );
}

export default GameDetail;
