// Loop Guard for Codex — mirrors .opencode/plugins/loop-guard.ts.
// PreToolUse hook: denies prohibited shell commands and protected-path file access.
// Reuses the exact path policy from .opencode/plugins/path-policy.mjs.
import { readFileSync } from "node:fs";
import { isProtectedPath, patchPaths } from "../../.opencode/plugins/path-policy.mjs";

const blocked = [
  /\bgit\s+push\b/i,
  /\bgit\s+reset\s+--hard\b/i,
  /\bgit\s+clean\b/i,
  /\brm\s+-rf\b/i,
  /\bdel\s+\/s\b/i,
  /\bformat\s+[a-z]:/i,
  /\bcurl\b/i,
  /\bwget\b/i,
  /\bInvoke-WebRequest\b/i,
  /\bInvoke-RestMethod\b/i,
  /\b(iwr|irm)\b/i,
  /\b(npm|bun|pip|pip3)\s+install\b/i,
  /\b(pnpm|yarn)\s+(install|add)\b/i,
  /\bpython\s+-m\s+pip\s+install\b/i,
  /\bgo\s+get\b/i,
];

function deny(reason) {
  process.stdout.write(
    JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: reason,
      },
    })
  );
  process.exit(0);
}

try {
  const input = JSON.parse(readFileSync(0, "utf8") || "{}");
  const tool = String(input.tool_name || "");
  const ti = input.tool_input || {};

  if (/shell|bash|powershell|cmd/i.test(tool)) {
    const cmd = String(ti.command ?? ti.cmd ?? "");
    if (blocked.some((re) => re.test(cmd))) {
      deny("LoopGuard blocked prohibited shell command");
    }
  }

  // Match both plain and namespaced file tool names (e.g. "Read",
  // "functions.read_file", "apply_patch", "functions.apply_patch").
  const toolName = tool.toLowerCase();
  const isFileTool =
    toolName.includes("read") ||
    toolName.includes("edit") ||
    toolName.includes("write") ||
    toolName.includes("apply_patch");
  if (isFileTool) {
    const file = String(ti.filePath ?? ti.path ?? ti.file ?? "");
    if (file && isProtectedPath(file)) {
      deny("LoopGuard blocked protected path");
    }
  }

  const patch = String(ti.patchText ?? "");
  if (patch && patchPaths(patch).some(isProtectedPath)) {
    deny("LoopGuard blocked patch to protected path");
  }
} catch {
  // Fail open on malformed input, matching the original guard: only explicit matches block.
}
