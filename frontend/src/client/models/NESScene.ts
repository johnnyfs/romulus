/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NESColor } from './NESColor';
import type { NESRef } from './NESRef';
export type NESScene = {
    background_color: NESColor;
    background_palettes?: (NESRef | null);
    sprite_palettes?: (NESRef | null);
    components?: Array<NESRef>;
};

