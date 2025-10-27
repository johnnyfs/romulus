/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetCreateRequest } from '../models/AssetCreateRequest';
import type { AssetListResponse } from '../models/AssetListResponse';
import type { AssetResponse } from '../models/AssetResponse';
import type { GroupedAssetCreateRequest } from '../models/GroupedAssetCreateRequest';
import type { GroupedAssetListResponse } from '../models/GroupedAssetListResponse';
import type { GroupedAssetResponse } from '../models/GroupedAssetResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AssetsService {
    /**
     * Create Asset
     * Create a new raw asset.
     * @param requestBody
     * @returns AssetResponse Successful Response
     * @throws ApiError
     */
    public static createAssetApiV1AssetsPost(
        requestBody: AssetCreateRequest,
    ): CancelablePromise<AssetResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/assets',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Assets
     * List all raw assets.
     * @param skip
     * @param limit
     * @returns AssetListResponse Successful Response
     * @throws ApiError
     */
    public static listAssetsApiV1AssetsGet(
        skip?: number,
        limit: number = 100,
    ): CancelablePromise<AssetListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/assets',
            query: {
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Asset
     * Get a specific raw asset.
     * @param assetId
     * @returns AssetResponse Successful Response
     * @throws ApiError
     */
    public static getAssetApiV1AssetsAssetIdGet(
        assetId: number,
    ): CancelablePromise<AssetResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/assets/{asset_id}',
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
     * Delete a raw asset.
     * @param assetId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteAssetApiV1AssetsAssetIdDelete(
        assetId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/assets/{asset_id}',
            path: {
                'asset_id': assetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Grouped Asset
     * Create a new grouped/processed asset.
     * @param requestBody
     * @returns GroupedAssetResponse Successful Response
     * @throws ApiError
     */
    public static createGroupedAssetApiV1AssetsGroupedPost(
        requestBody: GroupedAssetCreateRequest,
    ): CancelablePromise<GroupedAssetResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/assets/grouped',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Grouped Assets
     * List grouped assets, optionally filtered by raw_id.
     * @param rawId
     * @param skip
     * @param limit
     * @returns GroupedAssetListResponse Successful Response
     * @throws ApiError
     */
    public static listGroupedAssetsApiV1AssetsGroupedGet(
        rawId?: number,
        skip?: number,
        limit: number = 100,
    ): CancelablePromise<GroupedAssetListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/assets/grouped',
            query: {
                'raw_id': rawId,
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Grouped Asset
     * Get a specific grouped asset.
     * @param groupedId
     * @returns GroupedAssetResponse Successful Response
     * @throws ApiError
     */
    public static getGroupedAssetApiV1AssetsGroupedGroupedIdGet(
        groupedId: number,
    ): CancelablePromise<GroupedAssetResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/assets/grouped/{grouped_id}',
            path: {
                'grouped_id': groupedId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
