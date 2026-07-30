# ModelOffice

安全的代码执行沙箱系统，用于在隔离环境中执行用户代码。

## 📚 文档导航

- **[快速开始 (QUICKSTART.md)](QUICKSTART.md)** - 5分钟上手指南
- **[功能规格 (SPEC_ModelOffice_v1.md)](../docs/SPEC_ModelOffice_v1.md)** - 完整需求文档
- **[重构报告 (REFACTOR_COMPLETE.md)](REFACTOR_COMPLETE.md)** - 重构总结和验证
- **[演示脚本 (demo.py)](demo.py)** - 功能演示代码
- **[测试套件 (tests/)](tests/)** - 单元测试和集成测试

## 功能特性

- ✅ **Python 沙箱**: 基于 venv + subprocess 的轻量级隔离
- ✅ **网络隔离**: 支持完全禁用、白名单或完全开放
- ✅ **文件系统隔离**: 限制代码只能访问指定的 workspace 目录
- ✅ **资源限制**: 超时控制、内存限制（计划中）
- ✅ **安全策略**: 命令黑名单、参数过滤、路径验证
- ✅ **审计日志**: 记录所有执行命令和结果
- ✅ **环境管理**: 创建、克隆、销毁、快照
- ✅ **包管理**: 安装、卸载、列出已安装包
- ✅ **文件传输**: 上传、下载文件到/从 workspace

## 安装

```bash
pip install modeltoolbox-office
```

## 快速开始

### CLI 使用

```bash
# 创建环境
mtb office env create myenv

# 安装包
mtb office env install myenv requests pandas

# 列出已安装的包
mtb office env packages myenv

# 执行代码
mtb office exec myenv python -c "print('Hello from sandbox!')"

# 上传文件
mtb office upload myenv ./local.txt workspace/input/data.txt

# 下载文件
mtb office download myenv workspace/output/result.txt ./result.txt

# 创建快照
mtb office snapshot create myenv checkpoint-1

# 恢复快照
mtb office snapshot restore myenv checkpoint-1

# 克隆环境
mtb office env clone myenv myenv-copy

# 清理工作区
mtb office clean myenv

# 查看审计日志
mtb office audit --limit 20

# 销毁环境
mtb office env destroy myenv
```

### Python API

```python
from modeltoolbox_office import Sandbox

# 创建沙箱
sandbox = Sandbox.create("demo-env")

# 安装包
sandbox.install(["numpy", "pandas"])

# 执行代码
result = sandbox.execute("python script.py", timeout=60, network=False)
print(result["stdout"])
print(result["exit_code"])

# 上传文件
sandbox.upload("local.txt", "workspace/input/data.txt")

# 下载文件
sandbox.download("workspace/output/result.txt", "local_result.txt")

# 创建快照
sandbox.snapshot("checkpoint-1")

# 恢复快照
sandbox.restore("checkpoint-1")

# 清理工作区
sandbox.clean()

# 销毁环境
sandbox.destroy()
```

## 环境结构

每个沙箱环境在 `~/.modeltoolbox/office/envs/<env_name>/` 下：

```
<env_name>/
├── venv/              # Python 虚拟环境
│   ├── bin/python     # (Unix)
│   └── Scripts/python.exe  # (Windows)
└── workspace/         # 工作目录（用户代码只能访问此目录）
    ├── input/         # 输入文件
    ├── output/        # 输出文件
    └── temp/          # 临时文件
```

## 安全特性

### 命令黑名单

以下命令被阻止执行：

- 删除: `rm`, `rmdir`, `del`, `erase`
- 格式化: `format`, `mkfs`
- 系统: `shutdown`, `reboot`, `halt`
- 权限: `sudo`, `su`

### 参数黑名单

以下危险参数被阻止：

- `-rf`, `-fr` (递归强制删除)
- `/s`, `/q`, `/f` (Windows 强制删除)
- `--no-preserve-root` (删除根目录保护)

### 网络隔离

```python
# 完全禁用网络
sandbox.execute("python script.py", network=False)

# 或使用 CLI
mtb office exec myenv python script.py --no-network
```

网络禁用时，会设置以下环境变量：
- `NO_PROXY=*`
- `PIP_NO_INDEX=1`
- `MODELTOOLBOX_OFFICE_NETWORK=0`

### 审计日志

所有执行都会记录到 `~/.modeltoolbox/office/logs/audit.jsonl`：

```json
{
  "timestamp": "2026-07-28T12:00:00Z",
  "env": "demo-env",
  "command": ["python", "script.py"],
  "cwd": "/workspace",
  "exit_code": 0,
  "duration_ms": 1234,
  "stdout_length": 500,
  "stderr_length": 0,
  "network_allowed": false,
  "timeout_seconds": 60
}
```

## 使用场景

### 1. 用户代码执行

在 Web 应用中安全执行用户提交的代码：

```python
@app.post("/execute")
def execute_code(code: str, user_id: str):
    sandbox = Sandbox.create(f"user-{user_id}")
    sandbox.upload_text(code, "script.py")
    result = sandbox.execute("python script.py", timeout=30, network=False)
    sandbox.destroy()
    return result
```

### 2. AI Agent 代码执行

AI 生成代码并自动执行验证：

```python
def ai_coding_loop(task: str):
    sandbox = Sandbox.create("ai-sandbox")
    
    while not task_complete:
        code = ai_generate_code(task)
        sandbox.upload_text(code, "generated.py")
        result = sandbox.execute("python generated.py")
        
        if result["exit_code"] == 0:
            break
        else:
            task = f"{task}\nError: {result['stderr']}"
    
    sandbox.destroy()
```

### 3. 自动化测试

在 CI/CD 中隔离测试环境：

```yaml
- name: Run tests in sandbox
  run: |
    mtb office env create test-env
    mtb office env install test-env pytest
    mtb office upload test-env ./tests workspace/tests
    mtb office exec test-env pytest workspace/tests
```

## 限制和注意事项

1. **平台支持**: 目前支持 Windows、Linux、macOS
2. **资源限制**: Windows 不支持内存和 CPU 限制（需要 WSL 或容器）
3. **GUI 程序**: 不支持图形界面程序（仅 headless 模式）
4. **实时流式输出**: 目前批量返回，不支持实时流式输出

## 性能指标

- 创建环境: < 10 秒
- 执行命令开销: < 1 秒
- 并发环境: 支持 100+ 个并发环境

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/

# 类型检查
mypy modeltoolbox_office/
```

## 许可证

MIT License

## 相关项目

- [ModelCore](../ModelCore): 核心工具库
- [ModelMCP](../ModelMCP): MCP 服务器集成
