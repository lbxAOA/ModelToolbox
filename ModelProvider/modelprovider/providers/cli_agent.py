"""CLI Agent 适配器：通过本地已登录的编码助手 CLI（Claude Code / OpenAI Codex）
获取文本补全，无需单独申请 API key —— 直接复用终端里已经认证好的会话/订阅。

约定：
- 用 ``subprocess``（无 shell）调用本地可执行文件（默认 "claude" / "codex"，
  需在 PATH 中，且需已完成登录/认证 —— 这是用户终端里的既有状态，本模块不做认证，
  也不会以 shell=True 拼接命令，避免命令注入）。
- 命令行模板（:data:`ProviderSpec.cli_argv`）可用环境变量整体覆盖
  （见 :data:`ProviderSpec.cli_argv_env`），以适配不同版本 CLI 的实际参数——
  这类工具的 flag 迭代较快，硬编码容易过期。
- 多模态（图像）暂不支持：CLI 侧一般不接受内联图像输入，遇到图像分片会被忽略
  （只取文本），不抛错，方便与其它 provider 复用同一套调用代码。
- 无法保证 usage/token 统计（CLI 一般不暴露），:class:`~modelprovider.types.Usage`
  置 0；完整 stdout/stderr/argv 保留在 ``ChatResponse.raw`` 便于排查。
"""
from __future__ import annotations

import os
import shlex
import shutil
import subprocess

from ..base import Provider
from ..config import ResolvedConfig
from ..types import ChatRequest, ChatResponse, Usage


class CLIAgentError(RuntimeError):
    """调用本地 CLI 失败（未安装 / 未登录 / 非零退出码 / 超时）。"""


_DEFAULT_ARGV = ("{bin}", "-p", "{prompt}")
_DEFAULT_TIMEOUT = 300.0


def _build_argv(cfg: ResolvedConfig, prompt: str) -> list[str]:
    spec = cfg.spec
    template = spec.cli_argv or _DEFAULT_ARGV
    if spec.cli_argv_env:
        override = os.environ.get(spec.cli_argv_env)
        if override:
            template = tuple(shlex.split(override))
    bin_path = cfg.base_url  # cli_agent 场景下 base_url 复用为可执行文件路径/名
    return [
        tok.replace("{bin}", bin_path).replace("{prompt}", prompt).replace("{model}", cfg.model or "")
        for tok in template
    ]


class CLIAgentProvider(Provider):
    def chat(self, request: ChatRequest) -> ChatResponse:
        cfg = self.config
        system_txt = "\n".join(m.text() for m in request.messages if m.role == "system")
        user_txt = "\n".join(m.text() for m in request.messages if m.role != "system")
        prompt = f"{system_txt}\n\n{user_txt}".strip() if system_txt else user_txt

        argv = _build_argv(cfg, prompt)
        timeout = request.extra.get("timeout", _DEFAULT_TIMEOUT)
        try:
            proc = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        except FileNotFoundError as exc:
            raise CLIAgentError(
                f"未找到可执行文件 {argv[0]!r}；请确认已安装并登录 {cfg.spec.name} CLI，"
                f"或用 {cfg.spec.base_env} 指定其完整路径"
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise CLIAgentError(f"{cfg.spec.name} CLI 调用超时（{timeout}s）") from exc

        if proc.returncode != 0:
            raise CLIAgentError(
                f"{cfg.spec.name} CLI 退出码 {proc.returncode}: {proc.stderr.strip()[:500]}"
            )

        text = proc.stdout.strip()
        return ChatResponse(
            text=text,
            model=cfg.model or cfg.spec.name,
            provider=self.name,
            usage=Usage(),
            raw={"stdout": proc.stdout, "stderr": proc.stderr, "argv": argv},
        )

    def ping(self) -> bool:
        # 轻量连通性检查：只确认可执行文件可被找到，不实际调用模型
        # （避免每次 ping 都产生一次真实的 agent 调用/等待）。
        bin_path = self.config.base_url
        if shutil.which(bin_path) is None and not os.path.isfile(bin_path):
            raise CLIAgentError(
                f"未找到可执行文件 {bin_path!r}，请确认已安装 {self.name} CLI 并在 PATH 中"
            )
        return True
