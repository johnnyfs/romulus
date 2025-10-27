import React, { useEffect, useRef, useState } from 'react';
import styles from './ColorPicker.module.css';
import { NES_COLORS } from '../constants/nesColors';

interface ColorPickerProps {
  selectedIndex: number;
  onSelect: (index: number) => void;
  onClose: () => void;
  anchorEl: HTMLElement | null;
}

function ColorPicker({ selectedIndex, onSelect, onClose, anchorEl }: ColorPickerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState<{ top: number; left: number } | null>(null);

  useEffect(() => {
    if (anchorEl && containerRef.current) {
      const anchorRect = anchorEl.getBoundingClientRect();
      const containerRect = containerRef.current.getBoundingClientRect();

      let top = anchorRect.bottom + 8; // 8px below the anchor
      let left = anchorRect.left;

      // Adjust if it goes off the right edge
      if (left + containerRect.width > window.innerWidth) {
        left = window.innerWidth - containerRect.width - 16;
      }

      // Adjust if it goes off the bottom
      if (top + containerRect.height > window.innerHeight) {
        top = anchorRect.top - containerRect.height - 8; // Above the anchor instead
      }

      // Ensure it doesn't go off the left edge
      if (left < 16) {
        left = 16;
      }

      // Ensure it doesn't go off the top
      if (top < 16) {
        top = 16;
      }

      setPosition({ top, left });
    }
  }, [anchorEl]);

  const handleColorClick = (index: number) => {
    onSelect(index);
    onClose();
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    // Only close if clicking the backdrop, not the palette
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className={styles.colorPickerBackdrop} onClick={handleBackdropClick}>
      <div
        ref={containerRef}
        className={styles.colorPickerContainer}
        style={position ? { position: 'fixed', top: `${position.top}px`, left: `${position.left}px` } : {}}
      >
        <div className={styles.colorPickerHeader}>
          <span>Select NES Color</span>
          <button
            className={styles.colorPickerCloseButton}
            onClick={onClose}
            aria-label="Close"
          >
            ×
          </button>
        </div>
        <div className={styles.colorPickerGrid}>
          {NES_COLORS.map((color, index) => (
            <button
              key={index}
              className={`${styles.colorPickerSwatch} ${
                index === selectedIndex ? styles.colorPickerSwatchSelected : ''
              }`}
              style={{ backgroundColor: color }}
              onClick={() => handleColorClick(index)}
              title={`Color ${index.toString(16).toUpperCase().padStart(2, '0')}: ${color}`}
              aria-label={`Color ${index}`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default ColorPicker;
