/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ImageResourceData } from './ImageResourceData';
/**
 * Response after creating a resource.
 */
export type ResourceCreateResponse = {
    id: string;
    storage_key: string;
    resource_data: ImageResourceData;
    download_url: string;
};

