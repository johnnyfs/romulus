/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CompiledAssetType } from './CompiledAssetType';
import type { NESPaletteCompiledData_Input } from './NESPaletteCompiledData_Input';
/**
 * Request to create a compiled asset.
 */
export type CompiledAssetCreateRequest = {
    name: string;
    type: CompiledAssetType;
    data: NESPaletteCompiledData_Input;
};

