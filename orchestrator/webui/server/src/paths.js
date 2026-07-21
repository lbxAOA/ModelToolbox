import path from "node:path";
import { REPO_ROOT } from "./config.js";

/**
 * 把用户传入的相对路径解析到仓库根目录下，并校验结果仍在仓库根内，
 * 防止 `..` 路径穿越读写到仓库外的文件（OWASP 路径穿越）。
 * 传入非法（穿越出根目录）时抛错，调用方应捕获并返回 400。
 */
export function resolveInRepo(relPath) {
  if (typeof relPath !== "string" || relPath.trim() === "") {
    throw new Error("路径不能为空");
  }
  const normalizedRel = relPath.replace(/^[/\\]+/, ""); // 去掉开头的 / 或 \，防止被当成绝对路径逃逸
  const resolved = path.resolve(REPO_ROOT, normalizedRel);
  const rootWithSep = REPO_ROOT.endsWith(path.sep) ? REPO_ROOT : REPO_ROOT + path.sep;
  if (resolved !== REPO_ROOT && !resolved.startsWith(rootWithSep)) {
    throw new Error(`路径越界：${relPath}`);
  }
  return resolved;
}

/** 校验字符串只包含路径/标识符里允许的安全字符，防止参数注入到命令行标志位。 */
export function isSafeToken(value, pattern = /^[\w.,:@/\\ -]{1,300}$/u) {
  return typeof value === "string" && pattern.test(value);
}
