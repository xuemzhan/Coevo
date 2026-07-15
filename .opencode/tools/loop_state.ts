import { tool } from "@opencode-ai/plugin"
import path from "node:path"
import { spawn } from "node:child_process"

export default tool({
  description: "Atomically update the controlled loop state.",
  args: { phase: tool.schema.string(), status: tool.schema.string(), current_story: tool.schema.string().optional(), current_item: tool.schema.string().nullable().optional(), failed_verifications: tool.schema.number().int().min(0).optional(), blocking_issue: tool.schema.string().nullable().optional() },
  async execute(args, context) {
    const script=path.join(context.worktree,"scripts","loop_state.py")
    return await new Promise<string>((resolve,reject)=>{ const p=spawn("python",[script,"--stdin"],{cwd:context.worktree}); let out="",err=""; p.stdout.on("data",c=>out+=c); p.stderr.on("data",c=>err+=c); p.on("error",reject); p.on("close",code=>code===0?resolve(out.trim()):reject(new Error(`loop_state failed (${code}): ${err}`))); p.stdin.end(JSON.stringify(args)) })
  },
})
