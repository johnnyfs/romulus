/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GameCreateRequest } from '../models/GameCreateRequest';
import type { GameCreateResponse } from '../models/GameCreateResponse';
import type { GameDeleteResponse } from '../models/GameDeleteResponse';
import type { GameGetResponse } from '../models/GameGetResponse';
import type { GameListItem } from '../models/GameListItem';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class GamesService {
    /**
     * List Games
     * @returns GameListItem Successful Response
     * @throws ApiError
     */
    public static listGamesApiV1GamesGet(): CancelablePromise<Array<GameListItem>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/games',
        });
    }
    /**
     * Create Game
     * @param requestBody
     * @param _default
     * @returns GameCreateResponse Successful Response
     * @throws ApiError
     */
    public static createGameApiV1GamesPost(
        requestBody: GameCreateRequest,
        _default: boolean = false,
    ): CancelablePromise<GameCreateResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/games',
            query: {
                'default': _default,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Game
     * @param gameId
     * @returns GameGetResponse Successful Response
     * @throws ApiError
     */
    public static getGameApiV1GamesGameIdGet(
        gameId: string,
    ): CancelablePromise<GameGetResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/games/{game_id}',
            path: {
                'game_id': gameId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Game
     * @param gameId
     * @returns GameDeleteResponse Successful Response
     * @throws ApiError
     */
    public static deleteGameApiV1GamesGameIdDelete(
        gameId: string,
    ): CancelablePromise<GameDeleteResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/games/{game_id}',
            path: {
                'game_id': gameId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
