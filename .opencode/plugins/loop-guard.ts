import { isProtectedPath, patchPaths } from "./path-policy.mjs"

const blocked=[/\bgit\s+push\b/i,/\bgit\s+reset\s+--hard\b/i,/\bgit\s+clean\b/i,/\brm\s+-rf\b/i,/\bdel\s+\/s\b/i,/\bformat\s+[a-z]:/i,/\bcurl\b/i,/\bwget\b/i,/\bInvoke-WebRequest\b/i,/\bInvoke-RestMethod\b/i,/\b(iwr|irm)\b/i,/\b(npm|bun|pip|pip3)\s+install\b/i,/\b(pnpm|yarn)\s+(install|add)\b/i,/\bpython\s+-m\s+pip\s+install\b/i,/\bgo\s+get\b/i]
export const LoopGuard=async()=>({
  "tool.execute.before":async(input:{tool:string},output:{args:Record<string,unknown>})=>{
    if(input.tool==="bash"&&blocked.some(pattern=>pattern.test(String(output.args.command??"")))) throw new Error("LoopGuard blocked prohibited shell command")
    if(["read","edit","write"].includes(input.tool)){
      const file=String(output.args.filePath??output.args.path??output.args.file??"")
      if(file&&isProtectedPath(file)) throw new Error("LoopGuard blocked protected path")
    }
    if(input.tool==="apply_patch"&&patchPaths(output.args.patchText??"").some(isProtectedPath)) throw new Error("LoopGuard blocked patch to protected path")
  }
})
