import { tool } from "@opencode-ai/plugin"
import path from "node:path"
import { spawn } from "node:child_process"

export default tool({
  description: "Run a fail-closed, allowlisted quality gate.",
  args: { target: tool.schema.enum(["fmt","lint","test","test-security","test-e2e","quality"]) },
  async execute(args, context) {
    const script=path.join(context.worktree,"scripts","quality_gate.py")
    return await new Promise<string>((resolve,reject)=>{ const p=spawn("python",[script,"--target",args.target],{cwd:context.worktree}); let out="",err=""; p.stdout.on("data",c=>out+=c); p.stderr.on("data",c=>err+=c); p.on("error",reject); p.on("close",code=>code===0?resolve(out.trim()):reject(new Error(`quality gate failed (${code}): ${err}${out}`))) })
  },
})
