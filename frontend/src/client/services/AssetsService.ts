/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetCreateRequest } from '../models/AssetCreateRequest';
import type { AssetCreateResponse } from '../models/AssetCreateResponse';
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
     * Create Asset
     * Finalize an asset upload with metadata.
     *
     * After the client has uploaded to the presigned URL, they should call this
     * endpoint with the storage_key and asset metadata to finalize the upload.
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
