/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NESEntity } from './NESEntity';
import type { NESPaletteData_Input } from './NESPaletteData_Input';
import type { NESSpriteData } from './NESSpriteData';
export type EntityResponse_Input = {
    id: string;
    game_id: string;
    name: string;
    entity_data: NESEntity;
    components?: Array<(NESPaletteData_Input | NESSpriteData)>;
};

