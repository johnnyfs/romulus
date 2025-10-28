/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ImageState } from '../models/ImageState';
import type { ResourceCreateRequest } from '../models/ResourceCreateRequest';
import type { ResourceCreateResponse } from '../models/ResourceCreateResponse';
import type { ResourceType } from '../models/ResourceType';
import type { ResourceUpdateRequest } from '../models/ResourceUpdateRequest';
import type { UploadTicketRequest } from '../models/UploadTicketRequest';
import type { UploadTicketResponse } from '../models/UploadTicketResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ResourcesService {
    /**
     * Get Upload Ticket
     * Get a presigned URL for uploading an resource.
     *
     * Returns an upload ticket containing:
     * - upload_url: Presigned URL where the client should PUT the file
     * - storage_key: Key to reference this upload when finalizing
     * - resource_id: The UUID that will be assigned to this resource
     * @param requestBody
     * @returns UploadTicketResponse Successful Response
     * @throws ApiError
     */
    public static getUploadTicketResourcesUploadPost(
        requestBody: UploadTicketRequest,
    ): CancelablePromise<UploadTicketResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/resources/upload',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Resources
     * List all resources with optional filtering.
     *
     * Query params:
     * - resource_type: Filter by type (e.g., 'image')
     * - state: Filter by processing state (e.g., 'raw', 'grouped', 'cleaned')
     * @param resourceType Filter by resource type
     * @param state Filter by image state (for image resources)
     * @returns ResourceCreateResponse Successful Response
     * @throws ApiError
     */
    public static listResourcesResourcesGet(
        resourceType?: (ResourceType | null),
        state?: (ImageState | null),
    ): CancelablePromise<Array<ResourceCreateResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/resources',
            query: {
                'resource_type': resourceType,
                'state': state,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Resource
     * Finalize an resource upload with metadata.
     *
     * After the client has uploaded to the presigned URL, they should call this
     * endpoint with the storage_key and resource metadata to finalize the upload.
     * This will:
     * 1. Verify the file exists in storage
     * 2. Create the database record
     * 3. Write metadata.json to storage for recovery
     * @param requestBody
     * @returns ResourceCreateResponse Successful Response
     * @throws ApiError
     */
    public static createResourceResourcesPost(
        requestBody: ResourceCreateRequest,
    ): CancelablePromise<ResourceCreateResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/resources',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Resource
     * Get an resource by ID.
     * @param resourceId
     * @returns ResourceCreateResponse Successful Response
     * @throws ApiError
     */
    public static getResourceResourcesResourceIdGet(
        resourceId: string,
    ): CancelablePromise<ResourceCreateResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/resources/{resource_id}',
            path: {
                'resource_id': resourceId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Resource
     * Update an resource's metadata.
     *
     * Typical use: Mark a raw resource as processed=true after creating grouped versions.
     * Updates both the database record and the metadata.json file in storage.
     * @param resourceId
     * @param requestBody
     * @returns ResourceCreateResponse Successful Response
     * @throws ApiError
     */
    public static updateResourceResourcesResourceIdPut(
        resourceId: string,
        requestBody: ResourceUpdateRequest,
    ): CancelablePromise<ResourceCreateResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/resources/{resource_id}',
            path: {
                'resource_id': resourceId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Resource
     * Delete an resource and its stored file.
     * @param resourceId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteResourceResourcesResourceIdDelete(
        resourceId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/resources/{resource_id}',
            path: {
                'resource_id': resourceId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
