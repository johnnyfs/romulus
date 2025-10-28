/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CompiledAssetType } from './CompiledAssetType';
import type { NESPaletteCompiledData_Output } from './NESPaletteCompiledData_Output';
/**
 * Response for a compiled asset.
 */
export type CompiledAssetResponse = {
    id: string;
    game_id: string;
    name: string;
    type: CompiledAssetType;
    data: NESPaletteCompiledData_Output;
};

