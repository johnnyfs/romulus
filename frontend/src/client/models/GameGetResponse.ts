/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetResponse } from './AssetResponse';
import type { EntityResponse_Output } from './EntityResponse_Output';
import type { NESGameData } from './NESGameData';
import type { SceneCreateResponse } from './SceneCreateResponse';
export type GameGetResponse = {
    name: string;
    id: string;
    game_data: NESGameData;
    scenes: Array<SceneCreateResponse>;
    assets: Array<AssetResponse>;
    entities: Array<EntityResponse_Output>;
};

