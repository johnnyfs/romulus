/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ComponentCreateRequest } from '../models/ComponentCreateRequest';
import type { ComponentCreateResponse } from '../models/ComponentCreateResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ComponentsService {
    /**
     * Create Component
     * @param gameId
     * @param requestBody
     * @returns ComponentCreateResponse Successful Response
     * @throws ApiError
     */
    public static createComponentApiV1GamesGameIdComponentsPost(
        gameId: string,
        requestBody: ComponentCreateRequest,
    ): CancelablePromise<ComponentCreateResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/games/{game_id}/components',
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
     * Delete Component
     * @param gameId
     * @param componentId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteComponentApiV1GamesGameIdComponentsComponentIdDelete(
        gameId: string,
        componentId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/games/{game_id}/components/{component_id}',
            path: {
                'game_id': gameId,
                'component_id': componentId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
