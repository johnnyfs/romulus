/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityCreateRequest } from '../models/EntityCreateRequest';
import type { EntityCreateResponse } from '../models/EntityCreateResponse';
import type { EntityUpdateRequest } from '../models/EntityUpdateRequest';
import type { EntityUpdateResponse } from '../models/EntityUpdateResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class EntitiesService {
    /**
     * Create Entity
     * @param sceneId
     * @param requestBody
     * @returns EntityCreateResponse Successful Response
     * @throws ApiError
     */
    public static createEntityGamesGameIdScenesSceneIdEntitiesPost(
        sceneId: string,
        requestBody: EntityCreateRequest,
    ): CancelablePromise<EntityCreateResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/games/{game_id}/scenes/{scene_id}/entities',
            path: {
                'scene_id': sceneId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Entity
     * @param sceneId
     * @param entityId
     * @param requestBody
     * @returns EntityUpdateResponse Successful Response
     * @throws ApiError
     */
    public static updateEntityGamesGameIdScenesSceneIdEntitiesEntityIdPut(
        sceneId: string,
        entityId: string,
        requestBody: EntityUpdateRequest,
    ): CancelablePromise<EntityUpdateResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/games/{game_id}/scenes/{scene_id}/entities/{entity_id}',
            path: {
                'scene_id': sceneId,
                'entity_id': entityId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Entity
     * @param sceneId
     * @param entityId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteEntityGamesGameIdScenesSceneIdEntitiesEntityIdDelete(
        sceneId: string,
        entityId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/games/{game_id}/scenes/{scene_id}/entities/{entity_id}',
            path: {
                'scene_id': sceneId,
                'entity_id': entityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
