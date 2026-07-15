import { tool } from "@opencode-ai/plugin"
import path from "node:path"
import { spawn } from "node:child_process"

export default tool({
  description: "Read-only AC-to-test traceability check.",
  args: { story: tool.schema.string().optional() },
  async execute(args, context) {
    const argv=[path.join(context.worktree,"scripts","traceability_check.py")]; if(args.story) argv.push("--story",args.story)
    return await new Promise<string>((resolve,reject)=>{ const p=spawn("python",argv,{cwd:context.worktree}); let out="",err=""; p.stdout.on("data",c=>out+=c); p.stderr.on("data",c=>err+=c); p.on("error",reject); p.on("close",code=>code===0?resolve(out.trim()):reject(new Error(`traceability check failed (${code}): ${err}${out}`))) })
  },
})
