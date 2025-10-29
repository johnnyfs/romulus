/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GameCreateRequest } from '../models/GameCreateRequest';
import type { GameCreateResponse } from '../models/GameCreateResponse';
import type { GameDeleteResponse } from '../models/GameDeleteResponse';
import type { GameGetResponse } from '../models/GameGetResponse';
import type { GameListItem_Output } from '../models/GameListItem_Output';
import type { GameUpdateRequest } from '../models/GameUpdateRequest';
import type { GameUpdateResponse } from '../models/GameUpdateResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class GamesService {
    /**
     * List Games
     * @returns GameListItem_Output Successful Response
     * @throws ApiError
     */
    public static listGamesGamesGet(): CancelablePromise<Array<GameListItem_Output>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/games',
        });
    }
    /**
     * Create Game
     * @param requestBody
     * @param _default
     * @returns GameCreateResponse Successful Response
     * @throws ApiError
     */
    public static createGameGamesPost(
        requestBody: GameCreateRequest,
        _default: boolean = false,
    ): CancelablePromise<GameCreateResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/games',
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
    public static getGameGamesGameIdGet(
        gameId: string,
    ): CancelablePromise<GameGetResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/games/{game_id}',
            path: {
                'game_id': gameId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Game
     * @param gameId
     * @param requestBody
     * @returns GameUpdateResponse Successful Response
     * @throws ApiError
     */
    public static updateGameGamesGameIdPut(
        gameId: string,
        requestBody: GameUpdateRequest,
    ): CancelablePromise<GameUpdateResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/games/{game_id}',
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
     * Delete Game
     * @param gameId
     * @returns GameDeleteResponse Successful Response
     * @throws ApiError
     */
    public static deleteGameGamesGameIdDelete(
        gameId: string,
    ): CancelablePromise<GameDeleteResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/games/{game_id}',
            path: {
                'game_id': gameId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Render Game
     * Renders a game into a NES ROM file.
     *
     * Returns the ROM data as application/octet-stream which can be
     * loaded directly into a NES emulator.
     * @param gameId
     * @returns any NES ROM binary data
     * @throws ApiError
     */
    public static renderGameGamesGameIdRenderPost(
        gameId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/games/{game_id}/render',
            path: {
                'game_id': gameId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
