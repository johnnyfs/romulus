/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AdminService {
    /**
     * List Raw Assets Json
     * Get raw sprite assets as JSON.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static listRawAssetsJsonAdminAssetsRawDataGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/admin/assets/raw/data',
        });
    }
    /**
     * List Raw Assets
     * List all raw sprite assets.
     * @returns string Successful Response
     * @throws ApiError
     */
    public static listRawAssetsAdminAssetsRawGet(): CancelablePromise<string> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/admin/assets/raw',
        });
    }
    /**
     * View Raw Asset Json
     * Get raw asset metadata and derived sprites as JSON.
     * @param filename
     * @returns any Successful Response
     * @throws ApiError
     */
    public static viewRawAssetJsonAdminAssetsRawFilenameDataGet(
        filename: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/admin/assets/raw/{filename}/data',
            path: {
                'filename': filename,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * View Raw Asset
     * View individual raw asset with metadata and derived sprites.
     * @param filename
     * @returns string Successful Response
     * @throws ApiError
     */
    public static viewRawAssetAdminAssetsRawFilenameGet(
        filename: string,
    ): CancelablePromise<string> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/admin/assets/raw/{filename}',
            path: {
                'filename': filename,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Grouped Assets Json
     * Get grouped sprite assets as JSON.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static listGroupedAssetsJsonAdminAssetsGroupedDataGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/admin/assets/grouped/data',
        });
    }
    /**
     * List Grouped Assets
     * List all grouped sprite assets.
     * @returns string Successful Response
     * @throws ApiError
     */
    public static listGroupedAssetsAdminAssetsGroupedGet(): CancelablePromise<string> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/admin/assets/grouped',
        });
    }
    /**
     * View Grouped Asset Json
     * Get grouped asset metadata as JSON.
     * @param filename
     * @returns any Successful Response
     * @throws ApiError
     */
    public static viewGroupedAssetJsonAdminAssetsGroupedFilenameDataGet(
        filename: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/admin/assets/grouped/{filename}/data',
            path: {
                'filename': filename,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * View Grouped Asset
     * View individual grouped asset with metadata.
     * @param filename
     * @returns string Successful Response
     * @throws ApiError
     */
    public static viewGroupedAssetAdminAssetsGroupedFilenameGet(
        filename: string,
    ): CancelablePromise<string> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/admin/assets/grouped/{filename}',
            path: {
                'filename': filename,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
