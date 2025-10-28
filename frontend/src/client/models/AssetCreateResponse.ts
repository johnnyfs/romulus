/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ImageAssetData } from './ImageAssetData';
/**
 * Response after creating an asset.
 */
export type AssetCreateResponse = {
    id: string;
    storage_key: string;
    asset_data: ImageAssetData;
    download_url: string;
};

