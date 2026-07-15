import path from "node:path"

function decodeBounded(value) {
  let current=String(value)
  for(let i=0;i<3;i++){
    let decoded
    try { decoded=decodeURIComponent(current) } catch { throw new Error("invalid percent encoding") }
    if(decoded===current) return current
    current=decoded
  }
  if(/%[0-9a-f]{2}/i.test(current)) throw new Error("excessively encoded path")
  return current
}

export function normalizedComponents(value) {
  const decoded=decodeBounded(value)
  if(decoded.includes("\0")) throw new Error("NUL in path")
  if(/^\\\\[.?]\\/i.test(decoded)||/^\/\/[.?]\//.test(decoded)) throw new Error("device path")
  const slashed=decoded.trim().replace(/^['"]|['"]$/g,"").replace(/\\/g,"/")
  const normalized=path.posix.normalize("/"+slashed.replace(/^[a-z]:/i,""))
  return normalized.toLowerCase().split("/").filter(Boolean)
}

export function isProtectedPath(value) {
  const parts=normalizedComponents(value)
  if(parts.includes("secure")||parts.includes("keys")) return true
  if(parts.some(part=>part===".env"||part.startsWith(".env."))) return true
  for(let i=0;i<parts.length-1;i++){
    if(parts[i]==="programdata"&&parts[i+1]==="opencode") return true
    if(parts[i]===".git"&&parts[i+1]==="hooks") return true
  }
  return false
}

export function patchPaths(patchText) {
  const paths=[]
  for(const line of String(patchText).split(/\r?\n/)){
    const match=line.match(/^\*\*\* (?:Add|Update|Delete) File:\s*(.+)$/)
    const move=line.match(/^\*\*\* Move to:\s*(.+)$/)
    if(match) paths.push(match[1].trim())
    if(move) paths.push(move[1].trim())
  }
  return paths
}
