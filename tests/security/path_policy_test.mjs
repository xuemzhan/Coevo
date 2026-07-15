import assert from "node:assert/strict"
import { isProtectedPath, patchPaths } from "../../.opencode/plugins/path-policy.mjs"

for(const value of ["secure/key.pem","./keys/x","safe/../keys/x","KEYS\\x","%6beys/x","safe/%2e%2e/keys/x","C:\\ProgramData\\OpenCode\\x",".git/hooks/pre-commit","config/.env.prod"]){ assert.equal(isProtectedPath(value),true,value) }
for(const value of ["environment.txt","safe/key.pem","config/env.example","monkeys/data.txt"]){ assert.equal(isProtectedPath(value),false,value) }
assert.throws(()=>isProtectedPath("\\\\?\\C:\\safe\\x"))
assert.deepEqual(patchPaths("*** Begin Patch\n*** Update File: safe/../keys/x\n*** Move to: secure/y\n*** End Patch"),["safe/../keys/x","secure/y"])
