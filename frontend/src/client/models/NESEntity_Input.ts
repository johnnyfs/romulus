/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NESPaletteData_Input } from './NESPaletteData_Input';
import type { NESSpriteData } from './NESSpriteData';
/**
 * An entity with position data and attached components.
 */
export type NESEntity_Input = {
    'x': number;
    'y': number;
    components?: Array<(NESPaletteData_Input | NESSpriteData)>;
};

