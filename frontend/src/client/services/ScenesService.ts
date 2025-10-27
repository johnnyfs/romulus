/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SceneCreateRequest } from '../models/SceneCreateRequest';
import type { SceneCreateResponse } from '../models/SceneCreateResponse';
import type { SceneDeleteResponse } from '../models/SceneDeleteResponse';
import type { SceneUpdateRequest } from '../models/SceneUpdateRequest';
import type { SceneUpdateResponse } from '../models/SceneUpdateResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ScenesService {
    /**
     * Create Scene
     * @param gameId
     * @param requestBody
     * @returns SceneCreateResponse Successful Response
     * @throws ApiError
     */
    public static createSceneApiV1GamesGameIdScenesPost(
        gameId: string,
        requestBody: SceneCreateRequest,
    ): CancelablePromise<SceneCreateResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/games/{game_id}/scenes',
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
     * Delete Scene
     * @param gameId
     * @param sceneId
     * @returns SceneDeleteResponse Successful Response
     * @throws ApiError
     */
    public static deleteSceneApiV1GamesGameIdScenesSceneIdDelete(
        gameId: string,
        sceneId: string,
    ): CancelablePromise<SceneDeleteResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/games/{game_id}/scenes/{scene_id}',
            path: {
                'game_id': gameId,
                'scene_id': sceneId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Scene
     * @param gameId
     * @param sceneId
     * @param requestBody
     * @returns SceneUpdateResponse Successful Response
     * @throws ApiError
     */
    public static updateSceneApiV1GamesGameIdScenesSceneIdPut(
        gameId: string,
        sceneId: string,
        requestBody: SceneUpdateRequest,
    ): CancelablePromise<SceneUpdateResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/games/{game_id}/scenes/{scene_id}',
            path: {
                'game_id': gameId,
                'scene_id': sceneId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
