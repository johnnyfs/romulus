/**
 * Default NES palette presets for common color schemes
 * Each palette set contains 4 sub-palettes, each with 3 colors
 * (index 0 is the background color, shown for reference but not editable in palette)
 */

// A single sub-palette has 3 colors (color 0 is always the background)
export type SubPalette = [number, number, number];

export interface PalettePreset {
  name: string;
  subPalettes: [SubPalette, SubPalette, SubPalette, SubPalette]; // 4 sub-palettes
}

export const PALETTE_PRESETS: PalettePreset[] = [
  {
    name: 'Classic Mario Set',
    subPalettes: [
      [0x16, 0x27, 0x18], // Mario (Red/Brown)
      [0x1A, 0x2A, 0x19], // Luigi (Green)
      [0x11, 0x21, 0x31], // Sky (Blue)
      [0x28, 0x38, 0x16], // Coin (Yellow/Gold)
    ],
  },
  {
    name: 'Fire & Ice Set',
    subPalettes: [
      [0x16, 0x26, 0x28], // Fire (Red/Orange/Yellow)
      [0x2C, 0x3C, 0x30], // Ice (Cyan/White)
      [0x14, 0x24, 0x34], // Purple/Pink
      [0x00, 0x10, 0x20], // Stone (Gray)
    ],
  },
  {
    name: 'Nature Set',
    subPalettes: [
      [0x1A, 0x2A, 0x28], // Grass (Green/Yellow)
      [0x18, 0x28, 0x38], // Earth (Brown/Tan)
      [0x11, 0x21, 0x31], // Water (Blue)
      [0x1A, 0x2A, 0x19], // Forest (Dark green)
    ],
  },
  {
    name: 'Grayscale Set',
    subPalettes: [
      [0x0D, 0x00, 0x10], // Black to gray
      [0x10, 0x20, 0x30], // Gray gradient
      [0x00, 0x10, 0x20], // Dark gray gradient
      [0x20, 0x30, 0x10], // Light gray gradient
    ],
  },
  {
    name: 'Sunset Set',
    subPalettes: [
      [0x27, 0x26, 0x35], // Orange/Red-Orange/Pink
      [0x14, 0x24, 0x34], // Purple/Pink
      [0x11, 0x21, 0x31], // Blue
      [0x16, 0x26, 0x14], // Orange/Yellow/Purple
    ],
  },
];

/**
 * Get a default palette preset by index
 */
export function getDefaultPalette(index: number = 0): PalettePreset {
  return PALETTE_PRESETS[index % PALETTE_PRESETS.length];
}
