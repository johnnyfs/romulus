/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityResponse } from './EntityResponse';
import type { NESScene } from './NESScene';
export type SceneUpdateResponse = {
    game_id: string;
    name: string;
    scene_data: NESScene;
    id: string;
    entities?: Array<EntityResponse>;
};

