/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NESEntity } from './NESEntity';
import type { NESPaletteData_Output } from './NESPaletteData_Output';
import type { NESSpriteData } from './NESSpriteData';
export type EntityCreateResponse = {
    id: string;
    game_id: string;
    name: string;
    entity_data: NESEntity;
    components?: Array<(NESPaletteData_Output | NESSpriteData)>;
};

