import React, { useRef, useEffect, useState } from 'react';
import styles from './NESEmulator.module.css';
// @ts-ignore - jsnes doesn't have type definitions
import jsnes from 'jsnes';

interface NESEmulatorProps {
  romData: Uint8Array | null;
  width?: number;
  height?: number;
}

function NESEmulator({ romData, width = 256, height = 240 }: NESEmulatorProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const nesRef = useRef<any>(null);
  const animationRef = useRef<number | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const audioBufferRef = useRef<Float32Array>(new Float32Array(4096));
  const audioBufferIndexRef = useRef(0);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize audio
  useEffect(() => {
    const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
    if (AudioContextClass) {
      audioContextRef.current = new AudioContextClass({ sampleRate: 44100 });
    }

    return () => {
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  // Initialize NES emulator
  useEffect(() => {
    if (!romData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const imageData = ctx.createImageData(256, 240);

    // Create NES instance with frame callback
    const nes = new jsnes.NES({
      onFrame: (frameBuffer: number[]) => {
        // Convert NES frame buffer to canvas image data
        // jsnes outputs in 0xAABBGGRR format, so we need to swap R and B
        for (let i = 0; i < frameBuffer.length; i++) {
          const pixel = frameBuffer[i];
          imageData.data[i * 4 + 0] = pixel & 0xff;         // R (was at end)
          imageData.data[i * 4 + 1] = (pixel >> 8) & 0xff;  // G (middle, unchanged)
          imageData.data[i * 4 + 2] = (pixel >> 16) & 0xff; // B (was at start)
          imageData.data[i * 4 + 3] = 0xff;                 // A
        }
        ctx.putImageData(imageData, 0, 0);
      },
      onAudioSample: (left: number, right: number) => {
        // Buffer audio samples and play when we have enough
        if (!audioContextRef.current) return;

        const buffer = audioBufferRef.current;
        const bufferIndex = audioBufferIndexRef.current;

        // Mix left and right channels to mono
        buffer[bufferIndex] = (left + right) / 2;
        audioBufferIndexRef.current++;

        // When buffer is full, play it
        if (audioBufferIndexRef.current >= buffer.length) {
          const audioContext = audioContextRef.current;
          const audioBuffer = audioContext.createBuffer(1, buffer.length, audioContext.sampleRate);
          const channelData = audioBuffer.getChannelData(0);

          for (let i = 0; i < buffer.length; i++) {
            channelData[i] = buffer[i];
          }

          const source = audioContext.createBufferSource();
          source.buffer = audioBuffer;
          source.connect(audioContext.destination);
          source.start();

          audioBufferIndexRef.current = 0;
        }
      }
    });

    try {
      // Load ROM - jsnes expects a binary string
      // Convert in chunks to avoid stack overflow with large ROMs
      let romString = '';
      const chunkSize = 0x8000; // 32KB chunks
      for (let i = 0; i < romData.length; i += chunkSize) {
        const chunk = romData.slice(i, i + chunkSize);
        romString += String.fromCharCode.apply(null, Array.from(chunk) as any);
      }

      nes.loadROM(romString);
      nesRef.current = nes;
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load ROM');
      console.error('Failed to load ROM:', err);
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [romData]);

  // Animation loop
  useEffect(() => {
    if (!nesRef.current || !isRunning) return;

    let lastTime = performance.now();
    const frameTime = 1000 / 60; // 60 FPS

    const frame = (currentTime: number) => {
      const deltaTime = currentTime - lastTime;

      if (deltaTime >= frameTime) {
        nesRef.current.frame();
        lastTime = currentTime - (deltaTime % frameTime);
      }

      if (isRunning) {
        animationRef.current = requestAnimationFrame(frame);
      }
    };

    animationRef.current = requestAnimationFrame(frame);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isRunning]);

  // Debug: Log PPU state every second
  useEffect(() => {
    if (!nesRef.current || !isRunning) return;

    const debugInterval = setInterval(() => {
      const nes = nesRef.current;
      if (!nes || !nes.ppu || !nes.ppu.vramMem) return;

      const ppu = nes.ppu;
      // Debug logging removed - was spamming console
    }, 1000); // Every second

    return () => clearInterval(debugInterval);
  }, [isRunning]);

  const handlePlay = () => {
    if (nesRef.current && !isRunning) {
      setIsRunning(true);
    }
  };

  const handlePause = () => {
    setIsRunning(false);
  };

  const handleReset = () => {
    if (nesRef.current) {
      nesRef.current.reset();
      setIsRunning(false);
    }
  };

  // Keyboard controls
  useEffect(() => {
    if (!nesRef.current) return;

    const keyMap: { [key: string]: number } = {
      'ArrowUp': jsnes.Controller.BUTTON_UP,
      'ArrowDown': jsnes.Controller.BUTTON_DOWN,
      'ArrowLeft': jsnes.Controller.BUTTON_LEFT,
      'ArrowRight': jsnes.Controller.BUTTON_RIGHT,
      'KeyZ': jsnes.Controller.BUTTON_A,      // Z = A
      'KeyX': jsnes.Controller.BUTTON_B,      // X = B
      'Enter': jsnes.Controller.BUTTON_START,
      'ShiftRight': jsnes.Controller.BUTTON_SELECT,
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      // Escape key pauses the emulator (only when running)
      if (e.code === 'Escape' && isRunning) {
        e.preventDefault();
        setIsRunning(false);
        return;
      }

      // Only capture game controls when emulator is running
      if (!isRunning) return;

      const button = keyMap[e.code];
      if (button !== undefined) {
        e.preventDefault();
        nesRef.current?.buttonDown(1, button);
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      // Only handle key up when emulator is running
      if (!isRunning) return;

      const button = keyMap[e.code];
      if (button !== undefined) {
        e.preventDefault();
        nesRef.current?.buttonUp(1, button);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [romData, isRunning]);

  if (error) {
    return (
      <div className={styles.nesEmulatorError}>
        Error: {error}
      </div>
    );
  }

  if (!romData) {
    return (
      <div className={styles.nesEmulatorNoRom}>
        No ROM loaded
      </div>
    );
  }

  return (
    <div className={styles.nesEmulatorContainer}>
      <div className={styles.nesEmulatorScreen}>
        <canvas
          ref={canvasRef}
          width={256}
          height={240}
          className={styles.nesEmulatorCanvas}
          style={{
            width: `${width}px`,
            height: `${height}px`,
          }}
        />
      </div>

      <div className={styles.nesEmulatorControls}>
        <button
          onClick={handlePlay}
          disabled={isRunning}
          className={`${styles.nesEmulatorButton} ${styles.nesEmulatorButtonPlay}`}
        >
          {isRunning ? 'Playing' : 'Play'}
        </button>
        <button
          onClick={handlePause}
          disabled={!isRunning}
          className={`${styles.nesEmulatorButton} ${styles.nesEmulatorButtonPause}`}
        >
          Pause
        </button>
        <button
          onClick={handleReset}
          className={`${styles.nesEmulatorButton} ${styles.nesEmulatorButtonReset}`}
        >
          Reset
        </button>
      </div>

      <div className={styles.nesEmulatorHelp}>
        Controls: Arrow Keys = D-Pad | Z = A | X = B | Enter = Start | Shift = Select | ESC = Pause
      </div>
    </div>
  );
}

export default NESEmulator;
