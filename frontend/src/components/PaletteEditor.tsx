import { useState } from 'react';
import { Save } from 'lucide-react';
import styles from './PaletteEditor.module.css';
import { getNESColor } from '../constants/nesColors';
import ColorPicker from './ColorPicker';

// A single sub-palette has 3 colors (color 0 is always the background)
export type SubPalette = [number, number, number];

export interface PaletteData {
  id?: string; // undefined if not saved yet
  name: string;
  subPalettes: [SubPalette, SubPalette, SubPalette, SubPalette]; // 4 sub-palettes
  isDirty: boolean;
}

interface PaletteEditorProps {
  palette: PaletteData;
  backgroundColorIndex: number; // From scene, shown in column 0 for reference
  onUpdate: (subPalettes: [SubPalette, SubPalette, SubPalette, SubPalette]) => void;
  onNameChange: (name: string) => void;
  onSave: () => void;
  onDelete?: () => void;
  isSaving?: boolean;
}

function PaletteEditor({
  palette,
  backgroundColorIndex,
  onUpdate,
  onNameChange,
  onSave,
  onDelete,
  isSaving = false,
}: PaletteEditorProps) {
  const [showColorPicker, setShowColorPicker] = useState<{ subPaletteIndex: number; colorSlot: number } | null>(null);
  const [colorPickerAnchor, setColorPickerAnchor] = useState<HTMLElement | null>(null);

  const handleColorClick = (subPaletteIndex: number, colorSlot: number, event: React.MouseEvent<HTMLButtonElement>) => {
    setShowColorPicker({ subPaletteIndex, colorSlot });
    setColorPickerAnchor(event.currentTarget);
  };

  const handleColorSelect = (subPaletteIndex: number, colorSlot: number, colorIndex: number) => {
    const newSubPalettes: [SubPalette, SubPalette, SubPalette, SubPalette] = palette.subPalettes.map(sp => [...sp]) as [SubPalette, SubPalette, SubPalette, SubPalette];
    newSubPalettes[subPaletteIndex][colorSlot] = colorIndex;
    onUpdate(newSubPalettes);
  };

  return (
    <div className={styles.paletteEditorContainer}>
      <div className={styles.paletteHeader}>
        <input
          type="text"
          className={styles.paletteNameInput}
          value={palette.name}
          onChange={(e) => onNameChange(e.target.value)}
          placeholder="Palette name"
        />
        <button
          className={`${styles.paletteSaveButton} ${
            palette.isDirty ? styles.paletteSaveButtonActive : ''
          }`}
          onClick={onSave}
          disabled={!palette.isDirty || isSaving}
          title={palette.isDirty ? 'Save palette set' : 'No changes to save'}
        >
          <Save size={14} />
        </button>
      </div>

      {/* Render all palettes in a single row */}
      <div className={styles.paletteRow}>
        {/* Background color shown once at the start */}
        <div className={styles.paletteGroup}>
          <div className={styles.paletteColorLabel}>BG</div>
          <div className={styles.paletteSwatches}>
            <div
              className={`${styles.paletteColorSwatch} ${styles.paletteColorSwatchDisabled}`}
              style={{ backgroundColor: getNESColor(backgroundColorIndex) }}
              title={`Background: $${backgroundColorIndex.toString(16).toUpperCase().padStart(2, '0')}`}
            />
          </div>
        </div>

        {/* All 4 sub-palettes in a row, showing only their 3 colors */}
        {palette.subPalettes.map((subPalette, subPaletteIndex) => (
          <div key={subPaletteIndex} className={styles.paletteGroup}>
            <div className={styles.paletteColorLabel}>{subPaletteIndex}</div>
            <div className={styles.paletteSwatches}>
              {subPalette.map((colorIndex, slot) => (
                <button
                  key={slot}
                  className={styles.paletteColorSwatch}
                  style={{ backgroundColor: getNESColor(colorIndex) }}
                  onClick={(e) => handleColorClick(subPaletteIndex, slot, e)}
                  title={`Palette ${subPaletteIndex}, Color ${slot + 1}: $${colorIndex.toString(16).toUpperCase().padStart(2, '0')}`}
                />
              ))}
            </div>
          </div>
        ))}
      </div>

      {showColorPicker !== null && (
        <ColorPicker
          selectedIndex={palette.subPalettes[showColorPicker.subPaletteIndex][showColorPicker.colorSlot]}
          onSelect={(colorIndex) => handleColorSelect(showColorPicker.subPaletteIndex, showColorPicker.colorSlot, colorIndex)}
          onClose={() => {
            setShowColorPicker(null);
            setColorPickerAnchor(null);
          }}
          anchorEl={colorPickerAnchor}
        />
      )}
    </div>
  );
}

export default PaletteEditor;
