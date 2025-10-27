/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetType } from './AssetType';
/**
 * Request to create a new raw asset.
 */
export type AssetCreateRequest = {
    url: string;
    source_url?: (string | null);
    type: AssetType;
};

