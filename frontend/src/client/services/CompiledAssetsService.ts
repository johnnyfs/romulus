/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CompiledAssetCreateRequest } from '../models/CompiledAssetCreateRequest';
import type { CompiledAssetResponse } from '../models/CompiledAssetResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class CompiledAssetsService {
    /**
     * Create Compiled Asset
     * Create a compiled asset.
     *
     * Compiled assets are final, ready-to-use game resources like palettes.
     * They don't require upload - just provide the name, type, and data.
     * @param gameId
     * @param requestBody
     * @returns CompiledAssetResponse Successful Response
     * @throws ApiError
     */
    public static createCompiledAssetGamesGameIdCompiledAssetsPost(
        gameId: string,
        requestBody: CompiledAssetCreateRequest,
    ): CancelablePromise<CompiledAssetResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/games/{game_id}/compiled_assets',
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
     * Get Compiled Asset
     * Get a compiled asset by ID.
     * @param gameId
     * @param compiledAssetId
     * @returns CompiledAssetResponse Successful Response
     * @throws ApiError
     */
    public static getCompiledAssetGamesGameIdCompiledAssetsCompiledAssetIdGet(
        gameId: string,
        compiledAssetId: string,
    ): CancelablePromise<CompiledAssetResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/games/{game_id}/compiled_assets/{compiled_asset_id}',
            path: {
                'game_id': gameId,
                'compiled_asset_id': compiledAssetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Compiled Asset
     * Delete a compiled asset.
     * @param gameId
     * @param compiledAssetId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteCompiledAssetGamesGameIdCompiledAssetsCompiledAssetIdDelete(
        gameId: string,
        compiledAssetId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/games/{game_id}/compiled_assets/{compiled_asset_id}',
            path: {
                'game_id': gameId,
                'compiled_asset_id': compiledAssetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Compiled Assets
     * List all compiled assets for a game.
     * @param gameId
     * @returns CompiledAssetResponse Successful Response
     * @throws ApiError
     */
    public static listCompiledAssetsGamesGameIdCompiledAssetsGet(
        gameId: string,
    ): CancelablePromise<Array<CompiledAssetResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/games/{game_id}/compiled_assets/',
            path: {
                'game_id': gameId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
