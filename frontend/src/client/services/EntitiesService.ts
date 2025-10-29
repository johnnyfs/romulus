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
     * @param gameId
     * @param requestBody
     * @returns EntityCreateResponse Successful Response
     * @throws ApiError
     */
    public static createEntityGamesGameIdEntitiesPost(
        gameId: string,
        requestBody: EntityCreateRequest,
    ): CancelablePromise<EntityCreateResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/games/{game_id}/entities',
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
     * Update Entity
     * @param gameId
     * @param entityId
     * @param requestBody
     * @returns EntityUpdateResponse Successful Response
     * @throws ApiError
     */
    public static updateEntityGamesGameIdEntitiesEntityIdPut(
        gameId: string,
        entityId: string,
        requestBody: EntityUpdateRequest,
    ): CancelablePromise<EntityUpdateResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/games/{game_id}/entities/{entity_id}',
            path: {
                'game_id': gameId,
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
     * @param gameId
     * @param entityId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteEntityGamesGameIdEntitiesEntityIdDelete(
        gameId: string,
        entityId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/games/{game_id}/entities/{entity_id}',
            path: {
                'game_id': gameId,
                'entity_id': entityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
