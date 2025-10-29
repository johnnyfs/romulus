/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetResponse } from './AssetResponse';
import type { ComponentCreateResponse } from './ComponentCreateResponse';
import type { EntityResponse } from './EntityResponse';
import type { NESGameData } from './NESGameData';
import type { SceneCreateResponse } from './SceneCreateResponse';
export type GameGetResponse = {
    name: string;
    id: string;
    game_data: NESGameData;
    scenes: Array<SceneCreateResponse>;
    assets: Array<AssetResponse>;
    entities: Array<EntityResponse>;
    components: Array<ComponentCreateResponse>;
};

