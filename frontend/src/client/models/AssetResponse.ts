/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetType } from './AssetType';
/**
 * Response for asset.
 */
export type AssetResponse = {
    id: number;
    url: string;
    source_url: (string | null);
    type: AssetType;
    created_at: string;
    updated_at: (string | null);
};

