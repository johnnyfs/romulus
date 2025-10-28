/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetCreateRequest } from '../models/AssetCreateRequest';
import type { AssetCreateResponse } from '../models/AssetCreateResponse';
import type { AssetType } from '../models/AssetType';
import type { AssetUpdateRequest } from '../models/AssetUpdateRequest';
import type { ImageState } from '../models/ImageState';
import type { UploadTicketRequest } from '../models/UploadTicketRequest';
import type { UploadTicketResponse } from '../models/UploadTicketResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AssetsService {
    /**
     * Get Upload Ticket
     * Get a presigned URL for uploading an asset.
     *
     * Returns an upload ticket containing:
     * - upload_url: Presigned URL where the client should PUT the file
     * - storage_key: Key to reference this upload when finalizing
     * - asset_id: The UUID that will be assigned to this asset
     * @param requestBody
     * @returns UploadTicketResponse Successful Response
     * @throws ApiError
     */
    public static getUploadTicketAssetsUploadPost(
        requestBody: UploadTicketRequest,
    ): CancelablePromise<UploadTicketResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/assets/upload',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Assets
     * List all assets with optional filtering.
     *
     * Query params:
     * - asset_type: Filter by type (e.g., 'image')
     * - state: Filter by processing state (e.g., 'raw', 'grouped', 'cleaned')
     * @param assetType Filter by asset type
     * @param state Filter by image state (for image assets)
     * @returns AssetCreateResponse Successful Response
     * @throws ApiError
     */
    public static listAssetsAssetsGet(
        assetType?: (AssetType | null),
        state?: (ImageState | null),
    ): CancelablePromise<Array<AssetCreateResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/assets',
            query: {
                'asset_type': assetType,
                'state': state,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Asset
     * Finalize an asset upload with metadata.
     *
     * After the client has uploaded to the presigned URL, they should call this
     * endpoint with the storage_key and asset metadata to finalize the upload.
     * This will:
     * 1. Verify the file exists in storage
     * 2. Create the database record
     * 3. Write metadata.json to storage for recovery
     * @param requestBody
     * @returns AssetCreateResponse Successful Response
     * @throws ApiError
     */
    public static createAssetAssetsPost(
        requestBody: AssetCreateRequest,
    ): CancelablePromise<AssetCreateResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/assets',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Asset
     * Get an asset by ID.
     * @param assetId
     * @returns AssetCreateResponse Successful Response
     * @throws ApiError
     */
    public static getAssetAssetsAssetIdGet(
        assetId: string,
    ): CancelablePromise<AssetCreateResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/assets/{asset_id}',
            path: {
                'asset_id': assetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Asset
     * Update an asset's metadata.
     *
     * Typical use: Mark a raw asset as processed=true after creating grouped versions.
     * Updates both the database record and the metadata.json file in storage.
     * @param assetId
     * @param requestBody
     * @returns AssetCreateResponse Successful Response
     * @throws ApiError
     */
    public static updateAssetAssetsAssetIdPut(
        assetId: string,
        requestBody: AssetUpdateRequest,
    ): CancelablePromise<AssetCreateResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/assets/{asset_id}',
            path: {
                'asset_id': assetId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Asset
     * Delete an asset and its stored file.
     * @param assetId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteAssetAssetsAssetIdDelete(
        assetId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/assets/{asset_id}',
            path: {
                'asset_id': assetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
