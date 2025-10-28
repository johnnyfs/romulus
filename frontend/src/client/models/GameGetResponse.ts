/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ComponentCreateResponse } from './ComponentCreateResponse';
import type { SceneCreateResponse } from './SceneCreateResponse';
export type GameGetResponse = {
    name: string;
    id: string;
    scenes: Array<SceneCreateResponse>;
    components: Array<ComponentCreateResponse>;
};

