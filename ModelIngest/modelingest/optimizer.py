"""
Ollama 模型优化器

使用本地 Ollama 模型对原始 Markdown 内容进行智能优化：
- 提取核心概念
- 生成结构化摘要
- 建立知识链接
- 统一格式规范
"""

import json
import re
import requests
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class OptimizeConfig:
    """优化配置"""
    model: str = "qwen2.5:7b"
    base_url: str = "http://localhost:11434"
    template: str = "knowledge_base"
    temperature: float = 0.3
    max_tokens: int = 4096
    parallel_workers: int = 4


class OllamaOptimizer:
    """Ollama 模型优化器"""

    def __init__(self, config: OptimizeConfig):
        self.config = config
        self._check_ollama()

    def _check_ollama(self):
        """检查 Ollama 服务是否可用"""
        try:
            response = requests.get(f"{self.config.base_url}/api/tags", timeout=2)
            if response.status_code != 200:
                raise ConnectionError("Ollama 服务未运行")

            # 检查模型是否存在
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]

            if not any(self.config.model in name for name in model_names):
                print(f"⚠️  模型 {self.config.model} 未安装，尝试拉取...")
                self._pull_model()

        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"无法连接到 Ollama 服务 ({self.config.base_url})\n"
                "请确保 Ollama 已启动：ollama serve"
            )

    def _pull_model(self):
        """拉取模型"""
        response = requests.post(
            f"{self.config.base_url}/api/pull",
            json={"name": self.config.model},
            stream=True
        )

        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "status" in data:
                    print(f"  {data['status']}")

    def optimize_note(self, content: str, source_path: Path) -> Dict:
        """优化单个笔记"""

        # 构建提示词
        prompt = self._build_prompt(content, str(source_path))

        # 调用 Ollama API
        try:
            response = requests.post(
                f"{self.config.base_url}/api/generate",
                json={
                    "model": self.config.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.config.temperature,
                        "num_predict": self.config.max_tokens
                    }
                },
                timeout=120
            )

            result = response.json()
            optimized = self._parse_response(result.get("response", ""))

            return {
                "success": True,
                "data": optimized,
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

    def _build_prompt(self, content: str, source: str) -> str:
        """构建优化提示词"""

        # 限制内容长度（避免超出上下文窗口）
        max_content_length = 8000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "\n\n...(内容过长，已截断)"

        if self.config.template == "knowledge_base":
            return f"""你是一个技术知识库优化助手。请将以下算法/数据结构相关的原始文档转换为结构化的知识库笔记。

要求：
1. 提取核心概念，用 [[双方括号]] 标记重要术语（用于建立知识链接）
2. 生成 100-200 字的核心摘要
3. 识别关键知识点并列出
4. 保留所有代码示例和数学公式
5. 使用清晰的 Markdown 格式
6. 添加 3-5 个相关标签

原始文档：
---
{content}
---

请以 JSON 格式输出（必须是有效的 JSON）：
{{
  "title": "笔记标题",
  "summary": "核心摘要（100-200字）",
  "tags": ["标签1", "标签2", "标签3"],
  "key_concepts": ["核心概念1", "核心概念2"],
  "content": "优化后的完整 Markdown 内容"
}}

注意：
- content 中使用 [[术语]] 标记重要概念
- 保留所有 ```代码块```
- 保留所有数学公式（$公式$）
- 使用标准 Markdown 标题层级（##, ###）
"""

        elif self.config.template == "tutorial":
            return f"""你是一个技术教程优化助手。请将以下内容转换为清晰的算法教程格式。

要求：
1. 使用"问题引入 → 核心思想 → 算法原理 → 代码实现 → 复杂度分析"结构
2. 标记关键术语：[[术语]]
3. 保留所有代码和公式
4. 添加难度级别和前置知识

原始内容：
---
{content}
---

输出 JSON（必须有效）：
{{
  "title": "教程标题",
  "difficulty": "初级/中级/高级",
  "prerequisites": ["前置知识1", "前置知识2"],
  "summary": "简介",
  "content": "优化后的完整内容"
}}
"""

    def _parse_response(self, response: str) -> Dict:
        """解析模型响应"""

        # 尝试提取 JSON
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # 降级：返回原始响应
        return {
            "title": "未解析",
            "summary": "",
            "tags": [],
            "key_concepts": [],
            "content": response
        }

    def optimize_batch(
        self,
        input_dir: Path,
        output_dir: Path,
        progress_callback=None
    ) -> Dict:
        """批量优化笔记"""

        output_dir.mkdir(parents=True, exist_ok=True)

        stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0
        }

        # 收集所有 Markdown 文件
        md_files = list(input_dir.rglob("*.md"))
        stats["total"] = len(md_files)

        for idx, md_file in enumerate(md_files, 1):
            if progress_callback:
                progress_callback(idx, stats["total"], md_file.name)

            try:
                # 读取原始内容
                content = md_file.read_text(encoding='utf-8', errors='ignore')

                # 跳过太短的文件
                if len(content.strip()) < 100:
                    stats["skipped"] += 1
                    continue

                # 优化
                result = self.optimize_note(content, md_file)

                if result["success"]:
                    # 保存优化后的内容
                    rel_path = md_file.relative_to(input_dir)
                    out_file = output_dir / rel_path
                    out_file.parent.mkdir(parents=True, exist_ok=True)

                    optimized_content = self._format_optimized(result["data"], str(md_file))
                    out_file.write_text(optimized_content, encoding='utf-8')

                    stats["success"] += 1
                else:
                    print(f"❌ 优化失败: {md_file.name} - {result['error']}")
                    stats["failed"] += 1

            except Exception as e:
                print(f"❌ 处理失败: {md_file.name} - {e}")
                stats["failed"] += 1

        return stats

    def _format_optimized(self, data: Dict, source: str) -> str:
        """格式化优化后的内容"""

        lines = []

        # Frontmatter
        lines.append("---")
        if data.get("title"):
            lines.append(f"title: {data['title']}")
        if data.get("tags"):
            tags_str = json.dumps(data['tags'], ensure_ascii=False)
            lines.append(f"tags: {tags_str}")
        if data.get("difficulty"):
            lines.append(f"difficulty: {data['difficulty']}")
        if data.get("prerequisites"):
            prereq_str = json.dumps(data['prerequisites'], ensure_ascii=False)
            lines.append(f"prerequisites: {prereq_str}")
        lines.append(f"source: {source}")
        lines.append("optimized: true")
        lines.append("optimizer: ollama")
        lines.append("---")
        lines.append("")

        # 标题
        if data.get("title"):
            lines.append(f"# {data['title']}")
            lines.append("")

        # 摘要
        if data.get("summary"):
            lines.append("## 📝 核心摘要")
            lines.append("")
            lines.append(data['summary'])
            lines.append("")

        # 关键概念
        if data.get("key_concepts"):
            lines.append("## 🔑 关键概念")
            lines.append("")
            for concept in data["key_concepts"]:
                lines.append(f"- [[{concept}]]")
            lines.append("")

        # 主要内容
        content = data.get("content", "")
        if content:
            lines.append("---")
            lines.append("")
            lines.append(content)

        return "\n".join(lines)


def optimize_knowledge_base(
    input_dir: Path,
    output_dir: Path,
    config: OptimizeConfig = None
) -> Dict:
    """便捷函数：优化知识库"""

    if config is None:
        config = OptimizeConfig()

    optimizer = OllamaOptimizer(config)

    print(f"🚀 开始优化知识库...")
    print(f"   输入: {input_dir}")
    print(f"   输出: {output_dir}")
    print(f"   模型: {config.model}")
    print()

    def progress(current, total, filename):
        print(f"  [{current}/{total}] 优化中: {filename}")

    stats = optimizer.optimize_batch(input_dir, output_dir, progress)

    print()
    print(f"✅ 优化完成！")
    print(f"   总计: {stats['total']}")
    print(f"   成功: {stats['success']}")
    print(f"   失败: {stats['failed']}")
    print(f"   跳过: {stats['skipped']}")

    return stats
