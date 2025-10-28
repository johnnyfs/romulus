/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ImageState } from './ImageState';
import type { ImageTag } from './ImageTag';
import type { ImageType } from './ImageType';
/**
 * Data for an image asset.
 */
export type ImageAssetData = {
    type?: string;
    state: ImageState;
    image_type: ImageType;
    tags?: Array<ImageTag>;
    source_url?: (string | null);
    license?: (string | null);
};

