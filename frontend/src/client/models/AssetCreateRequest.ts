/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetType } from './AssetType';
import type { NESPaletteAssetData_Input } from './NESPaletteAssetData_Input';
import type { NESSpriteSetAssetData } from './NESSpriteSetAssetData';
/**
 * Request to create an asset.
 */
export type AssetCreateRequest = {
    name: string;
    type: AssetType;
    data: (NESPaletteAssetData_Input | NESSpriteSetAssetData);
};

