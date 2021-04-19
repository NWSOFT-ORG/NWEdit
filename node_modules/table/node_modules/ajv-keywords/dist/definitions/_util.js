"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.usePattern = exports.metaSchemaRef = void 0;
const codegen_1 = require("ajv/dist/compile/codegen");
const META_SCHEMA_ID = "http://json-schema.org/schema";
function metaSchemaRef({ defaultMeta } = {}) {
    return defaultMeta === false ? {} : { $ref: defaultMeta || META_SCHEMA_ID };
}
exports.metaSchemaRef = metaSchemaRef;
function usePattern(gen, pattern, flags = "u") {
    return gen.scopeValue("pattern", {
        key: pattern,
        ref: new RegExp(pattern, flags),
        code: codegen_1._ `new RegExp(${pattern}, ${flags})`,
    });
}
exports.usePattern = usePattern;
//# sourceMappingURL=_util.js.map