/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NESPaletteData_Output } from './NESPaletteData_Output';
import type { NESSpriteData } from './NESSpriteData';
/**
 * An entity with position data and attached components.
 */
export type NESEntity_Output = {
    'x': number;
    'y': number;
    components?: Array<(NESPaletteData_Output | NESSpriteData)>;
};

