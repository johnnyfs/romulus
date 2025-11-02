import { useState } from 'react';
import { Save } from 'lucide-react';
import styles from './EntityEditor.module.css';
import type { AssetResponse } from '../client/models/AssetResponse';
import type { NESRef } from '../client/models/NESRef';

export interface EntityData {
  id?: string;
  name: string;
  x: number;
  y: number;
  spriteset: NESRef | null;
  palette_index: number;
  isDirty: boolean;
}

interface EntityEditorProps {
  entity: EntityData;
  onUpdate: (data: { x?: number; y?: number; spriteset?: NESRef | null; palette_index?: number }) => void;
  onNameChange: (name: string) => void;
  onSave: () => void;
  spriteSize: '8x8' | '8x16';  // Game's sprite size setting
  spriteSets: AssetResponse[];  // Available sprite set assets
  palettes: AssetResponse[];  // Available palette assets
  backgroundColor: number;  // Scene background color for preview
}

function EntityEditor({
  entity,
  onUpdate,
  onNameChange,
  onSave,
  spriteSets,
  palettes,
  backgroundColor
}: EntityEditorProps) {
  const [xInput, setXInput] = useState(entity.x.toString());
  const [yInput, setYInput] = useState(entity.y.toString());

  const handleXChange = (value: string) => {
    setXInput(value);
    const numValue = parseInt(value, 10);
    if (!isNaN(numValue) && numValue >= 0 && numValue <= 255) {
      onUpdate({ x: numValue });
    }
  };

  const handleYChange = (value: string) => {
    setYInput(value);
    const numValue = parseInt(value, 10);
    if (!isNaN(numValue) && numValue >= 0 && numValue <= 255) {
      onUpdate({ y: numValue });
    }
  };

  const handleSpriteSetChange = (spriteSetId: string) => {
    onUpdate({ spriteset: spriteSetId || null });
  };

  const handlePaletteIndexChange = (paletteIndex: number) => {
    onUpdate({ palette_index: paletteIndex });
  };

  // Decompile CHR data to pixel array (returns color indices 0-3)
  const decompileCHR = (chrData: Uint8Array): number[][] => {
    const pixels: number[][] = [];
    const bitplane0 = chrData.slice(0, 8);
    const bitplane1 = chrData.slice(8, 16);

    for (let row = 0; row < 8; row++) {
      const rowPixels: number[] = [];
      for (let col = 0; col < 8; col++) {
        const bitPos = 7 - col;
        const bit0 = (bitplane0[row] >> bitPos) & 1;
        const bit1 = (bitplane1[row] >> bitPos) & 1;
        const colorIndex = bit0 | (bit1 << 1);
        rowPixels.push(colorIndex);
      }
      pixels.push(rowPixels);
    }
    return pixels;
  };

  // Get NES color by index
  const getNESColor = (index: number): string => {
    // NES color palette (should match backend)
    const NES_COLORS = [
      '#7C7C7C', '#0000FC', '#0000BC', '#4428BC', '#940084', '#A80020', '#A81000', '#881400',
      '#503000', '#007800', '#006800', '#005800', '#004058', '#000000', '#000000', '#000000',
      '#BCBCBC', '#0078F8', '#0058F8', '#6844FC', '#D800CC', '#E40058', '#F83800', '#E45C10',
      '#AC7C00', '#00B800', '#00A800', '#00A844', '#008888', '#000000', '#000000', '#000000',
      '#F8F8F8', '#3CBCFC', '#6888FC', '#9878F8', '#F878F8', '#F85898', '#F87858', '#FCA044',
      '#F8B800', '#B8F818', '#58D854', '#58F898', '#00E8D8', '#787878', '#000000', '#000000',
      '#FCFCFC', '#A4E4FC', '#B8B8F8', '#D8B8F8', '#F8B8F8', '#F8A4C0', '#F0D0B0', '#FCE0A8',
      '#F8D878', '#D8F878', '#B8F8B8', '#B8F8D8', '#00FCFC', '#F8D8F8', '#000000', '#000000',
    ];
    return NES_COLORS[index % NES_COLORS.length] || '#000000';
  };

  // Render sprite preview as canvas
  const renderSpritePreview = (): React.ReactNode => {
    if (!entity.spriteset) return null;

    const spriteSet = spriteSets.find(s => s.id === entity.spriteset);
    if (!spriteSet || spriteSet.type !== 'sprite_set') return null;

    // Get CHR data from sprite set
    const data = spriteSet.data as any;
    if (!data || !data.chr_data) return null;

    // Get palette colors
    const palette = palettes.find(p => p.id && p.type === 'palette');
    let colors = [backgroundColor, 0x16, 0x27, 0x18]; // Default colors if no palette

    if (palette && palette.data) {
      const paletteData = palette.data as any;
      if (paletteData.palettes && paletteData.palettes[entity.palette_index]) {
        const subPalette = paletteData.palettes[entity.palette_index];
        colors = [
          backgroundColor, // Color 0 is always background
          subPalette.colors[0]?.index || 0x16,
          subPalette.colors[1]?.index || 0x27,
          subPalette.colors[2]?.index || 0x18,
        ];
      }
    }

    // Convert chr_data (base64 string or bytes) to Uint8Array
    let chrData: Uint8Array;
    if (typeof data.chr_data === 'string') {
      // If it's a string, decode from base64 or latin1
      // FastAPI returns bytes as a string with \u escape sequences
      const bytes: number[] = [];
      for (let i = 0; i < data.chr_data.length; i++) {
        bytes.push(data.chr_data.charCodeAt(i));
      }
      chrData = new Uint8Array(bytes);
    } else {
      // If it's already a Uint8Array or ArrayBuffer
      chrData = new Uint8Array(data.chr_data);
    }

    const pixels = decompileCHR(chrData);

    return (
      <canvas
        ref={(canvas) => {
          if (!canvas) return;

          const ctx = canvas.getContext('2d');
          if (!ctx) return;

          // Clear canvas
          ctx.clearRect(0, 0, 16, 16);

          // Draw pixels (2x scale)
          for (let y = 0; y < 8; y++) {
            for (let x = 0; x < 8; x++) {
              const colorIndex = pixels[y][x];
              ctx.fillStyle = getNESColor(colors[colorIndex]);
              ctx.fillRect(x * 2, y * 2, 2, 2);
            }
          }
        }}
        width={16}
        height={16}
        className={styles.spritePreview}
      />
    );
  };

  return (
    <div className={styles.entityEditor}>
      <div className={styles.entityHeader}>
        <input
          type="text"
          className={styles.entityName}
          value={entity.name}
          onChange={(e) => onNameChange(e.target.value)}
        />
        <button
          className={`${styles.entitySaveButton} ${entity.isDirty ? styles.entitySaveButtonActive : ''}`}
          onClick={onSave}
          disabled={!entity.isDirty}
          title={entity.isDirty ? 'Save entity' : 'No changes to save'}
        >
          <Save size={14} />
        </button>
      </div>
      <div className={styles.entityFields}>
        <div className={styles.entityField}>
          <label className={styles.entityLabel}>X:</label>
          <input
            type="number"
            className={styles.entityInput}
            value={xInput}
            onChange={(e) => handleXChange(e.target.value)}
            min="0"
            max="255"
          />
        </div>
        <div className={styles.entityField}>
          <label className={styles.entityLabel}>Y:</label>
          <input
            type="number"
            className={styles.entityInput}
            value={yInput}
            onChange={(e) => handleYChange(e.target.value)}
            min="0"
            max="255"
          />
        </div>
      </div>

      {/* Sprite section */}
      <div className={styles.spriteSection}>
        <div className={styles.spriteHeader}>
          <span className={styles.spriteTitle}>Sprite</span>
        </div>

        <div className={styles.spriteContent}>
          {entity.spriteset && renderSpritePreview()}
          <div className={styles.spriteFields}>
            <div className={styles.spriteField}>
              <label>Sprite Set:</label>
              <select
                value={entity.spriteset || ''}
                onChange={(e) => handleSpriteSetChange(e.target.value)}
              >
                <option value="">None</option>
                {spriteSets.map((ss) => (
                  <option key={ss.id} value={ss.id}>
                    {ss.name}
                  </option>
                ))}
              </select>
            </div>

            {entity.spriteset && (
              <div className={styles.spriteField}>
                <label>Palette:</label>
                <div className={styles.paletteSelector}>
                  {[0, 1, 2, 3].map((idx) => (
                    <label key={idx} className={styles.paletteOption}>
                      <input
                        type="radio"
                        name="palette"
                        value={idx}
                        checked={entity.palette_index === idx}
                        onChange={() => handlePaletteIndexChange(idx)}
                      />
                      <span>{idx}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default EntityEditor;
