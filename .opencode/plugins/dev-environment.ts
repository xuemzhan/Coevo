import { createHash } from "node:crypto"
import fs from "node:fs"
import path from "node:path"

export default async ({ directory }: { directory: string }) => ({
  "shell.env": async (_input: unknown, output: { env: Record<string, string> }) => {
    const required={
      COEVO_MAKE_PATH: process.env.COEVO_MAKE_PATH,
      COEVO_MAKE_SHA256: process.env.COEVO_MAKE_SHA256,
      COEVO_EXTERNAL_MAKE_PATH: process.env.COEVO_EXTERNAL_MAKE_PATH,
      COEVO_EXTERNAL_MAKE_SHA256: process.env.COEVO_EXTERNAL_MAKE_SHA256,
      COEVO_PYTHON_PATH: process.env.COEVO_PYTHON_PATH,
      COEVO_PYTHON_SHA256: process.env.COEVO_PYTHON_SHA256,
      COEVO_NODE_PATH: process.env.COEVO_NODE_PATH,
      COEVO_NODE_SHA256: process.env.COEVO_NODE_SHA256,
      COEVO_POWERSHELL_PATH: process.env.COEVO_POWERSHELL_PATH,
      COEVO_POWERSHELL_SHA256: process.env.COEVO_POWERSHELL_SHA256,
      COEVO_CONTROL_ARCHIVE: process.env.COEVO_CONTROL_ARCHIVE,
      COEVO_CONTROL_SHA256: process.env.COEVO_CONTROL_SHA256,
    }
    for(const [name,value] of Object.entries(required)){
      if(!value) throw new Error(`missing locked development environment value: ${name}`)
      output.env[name]=value
    }
    const lockedFiles:[string,string][]=[
      [required.COEVO_MAKE_PATH!,required.COEVO_MAKE_SHA256!],
      [required.COEVO_EXTERNAL_MAKE_PATH!,required.COEVO_EXTERNAL_MAKE_SHA256!],
      [required.COEVO_PYTHON_PATH!,required.COEVO_PYTHON_SHA256!],
      [required.COEVO_NODE_PATH!,required.COEVO_NODE_SHA256!],
      [required.COEVO_CONTROL_ARCHIVE!,required.COEVO_CONTROL_SHA256!],
    ]
    for(const [candidate,expected] of lockedFiles){
      const resolved=path.resolve(candidate)
      if(!resolved.startsWith(path.resolve(directory)+path.sep)) throw new Error("locked tool escapes repository")
      const actual=createHash("sha256").update(fs.readFileSync(resolved)).digest("hex")
      if(actual!==expected) throw new Error(`locked tool hash mismatch: ${resolved}`)
    }
    // Locked tools remain absolute-path capabilities; never expose their writable sibling directory through PATH.
    for(const name of Object.keys(output.env)) if(name.toUpperCase().startsWith("PYTHON")) delete output.env[name]
    const psHash=createHash("sha256").update(fs.readFileSync(required.COEVO_POWERSHELL_PATH!)).digest("hex")
    if(psHash!==required.COEVO_POWERSHELL_SHA256) throw new Error("locked Windows PowerShell hash mismatch")
    output.env.COEVO_REPO_ROOT=path.resolve(directory)
    output.env.PYTHONNOUSERSITE="1"
    output.env.PYTHONDONTWRITEBYTECODE="1"
  },
})
