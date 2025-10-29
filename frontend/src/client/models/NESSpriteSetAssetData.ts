/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SpriteSetType } from './SpriteSetType';
/**
 * Data for a sprite set asset.
 *
 * A sprite set is a collection of CHR tiles that form animation frames.
 * The type determines the animation pattern and tile layout requirements.
 *
 * CHR data format:
 * - Each 8x8 tile is 16 bytes (2 bitplanes of 8 bytes each)
 * - For STATIC type: exactly 16 bytes (one 8x8 tile)
 * - Future animation types will require multiple tiles
 */
export type NESSpriteSetAssetData = {
    type?: string;
    sprite_set_type: SpriteSetType;
    chr_data: Blob;
};

