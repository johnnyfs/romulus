/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetCreateRequest } from '../models/AssetCreateRequest';
import type { AssetResponse } from '../models/AssetResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AssetsService {
    /**
     * Create Asset
     * Create a game asset.
     *
     * Game assets are final, ready-to-use game resources like palettes.
     * They don't require upload - just provide the name, type, and data.
     * @param gameId
     * @param requestBody
     * @returns AssetResponse Successful Response
     * @throws ApiError
     */
    public static createAssetGamesGameIdAssetsPost(
        gameId: string,
        requestBody: AssetCreateRequest,
    ): CancelablePromise<AssetResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/games/{game_id}/assets',
            path: {
                'game_id': gameId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Asset
     * Get a game asset by ID.
     * @param gameId
     * @param assetId
     * @returns AssetResponse Successful Response
     * @throws ApiError
     */
    public static getAssetGamesGameIdAssetsAssetIdGet(
        gameId: string,
        assetId: string,
    ): CancelablePromise<AssetResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/games/{game_id}/assets/{asset_id}',
            path: {
                'game_id': gameId,
                'asset_id': assetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Asset
     * Update a game asset.
     * @param gameId
     * @param assetId
     * @param requestBody
     * @returns AssetResponse Successful Response
     * @throws ApiError
     */
    public static updateAssetGamesGameIdAssetsAssetIdPut(
        gameId: string,
        assetId: string,
        requestBody: AssetCreateRequest,
    ): CancelablePromise<AssetResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/games/{game_id}/assets/{asset_id}',
            path: {
                'game_id': gameId,
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
     * Delete a game asset.
     * @param gameId
     * @param assetId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteAssetGamesGameIdAssetsAssetIdDelete(
        gameId: string,
        assetId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/games/{game_id}/assets/{asset_id}',
            path: {
                'game_id': gameId,
                'asset_id': assetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Assets
     * List all game assets for a game.
     * @param gameId
     * @returns AssetResponse Successful Response
     * @throws ApiError
     */
    public static listAssetsGamesGameIdAssetsGet(
        gameId: string,
    ): CancelablePromise<Array<AssetResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/games/{game_id}/assets/',
            path: {
                'game_id': gameId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
