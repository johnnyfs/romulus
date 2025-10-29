/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetType } from './AssetType';
import type { NESPaletteAssetData_Output } from './NESPaletteAssetData_Output';
import type { NESSpriteSetAssetData } from './NESSpriteSetAssetData';
/**
 * Response for an asset.
 */
export type AssetResponse = {
    id: string;
    game_id: string;
    name: string;
    type: AssetType;
    data: (NESPaletteAssetData_Output | NESSpriteSetAssetData);
};

