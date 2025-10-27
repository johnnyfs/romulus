/**
 * The NES/Famicom 64-color palette
 * Hex values for each of the 64 colors (0x00 - 0x3F)
 */
export const NES_COLORS: readonly string[] = [
  '#7C7C7C', // 0x00
  '#0000FC', // 0x01
  '#0000BC', // 0x02
  '#4428BC', // 0x03
  '#940084', // 0x04
  '#A80020', // 0x05
  '#A81000', // 0x06
  '#881400', // 0x07
  '#503000', // 0x08
  '#007800', // 0x09
  '#006800', // 0x0A
  '#005800', // 0x0B
  '#004058', // 0x0C
  '#000000', // 0x0D
  '#000000', // 0x0E
  '#000000', // 0x0F
  '#BCBCBC', // 0x10
  '#0078F8', // 0x11
  '#0058F8', // 0x12
  '#6844FC', // 0x13
  '#D800CC', // 0x14
  '#E40058', // 0x15
  '#F83800', // 0x16
  '#E45C10', // 0x17
  '#AC7C00', // 0x18
  '#00B800', // 0x19
  '#00A800', // 0x1A
  '#00A844', // 0x1B
  '#008888', // 0x1C
  '#000000', // 0x1D
  '#000000', // 0x1E
  '#000000', // 0x1F
  '#F8F8F8', // 0x20
  '#3CBCFC', // 0x21
  '#6888FC', // 0x22
  '#9878F8', // 0x23
  '#F878F8', // 0x24
  '#F85898', // 0x25
  '#F87858', // 0x26
  '#FCA044', // 0x27
  '#F8B800', // 0x28
  '#B8F818', // 0x29
  '#58D854', // 0x2A
  '#58F898', // 0x2B
  '#00E8D8', // 0x2C
  '#787878', // 0x2D
  '#000000', // 0x2E
  '#000000', // 0x2F
  '#FCFCFC', // 0x30
  '#A4E4FC', // 0x31
  '#B8B8F8', // 0x32
  '#D8B8F8', // 0x33
  '#F8B8F8', // 0x34
  '#F8A4C0', // 0x35
  '#F0D0B0', // 0x36
  '#FCE0A8', // 0x37
  '#F8D878', // 0x38
  '#D8F878', // 0x39
  '#B8F8B8', // 0x3A
  '#B8F8D8', // 0x3B
  '#00FCFC', // 0x3C
  '#F8D8F8', // 0x3D
  '#000000', // 0x3E
  '#000000', // 0x3F
] as const;

/**
 * Get the hex color for a given NES color index
 */
export function getNESColor(index: number): string {
  if (index < 0 || index >= NES_COLORS.length) {
    return '#000000'; // Default to black for invalid indices
  }
  return NES_COLORS[index];
}
