import { Block } from '../primitives';
export declare type Transform = (Block: any) => Block;
export declare function flow(...transforms: Transform[]): Transform;
