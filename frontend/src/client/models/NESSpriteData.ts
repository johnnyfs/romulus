/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NESRef } from './NESRef';
/**
 * Data for a sprite component.
 *
 * Sprite dimensions are in sprite units:
 * - For 8x8 mode: 1 unit = 8 pixels
 * - For 8x16 mode: 1 unit = 8x16 pixels
 */
export type NESSpriteData = {
    type?: string;
    width: number;
    height: number;
    sprite_set?: (NESRef | null);
    palette_index?: number;
};

