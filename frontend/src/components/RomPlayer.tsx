import React from 'react';
import NESEmulator from './NESEmulator';

interface RomPlayerProps {
  gameId: string;
  romData: Uint8Array | null;
}

function RomPlayer({ gameId, romData }: RomPlayerProps) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      border: '1px solid #ddd',
      borderRadius: '4px',
      backgroundColor: '#fff',
      overflow: 'hidden'
    }}>
      <div style={{
        padding: '10px',
        borderBottom: '1px solid #ddd',
        backgroundColor: '#f5f5f5',
        fontWeight: 'bold'
      }}>
        ROM Player
      </div>

      <div style={{ flex: 1, overflow: 'hidden' }}>
        <NESEmulator romData={romData} width={512} height={480} />
      </div>
    </div>
  );
}

export default RomPlayer;
