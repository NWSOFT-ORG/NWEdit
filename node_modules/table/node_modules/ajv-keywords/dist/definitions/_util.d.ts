import type { DefinitionOptions } from "./_types";
import type { SchemaObject, CodeGen, Name } from "ajv";
export declare function metaSchemaRef({ defaultMeta }?: DefinitionOptions): SchemaObject;
export declare function usePattern(gen: CodeGen, pattern: string, flags?: string): Name;
