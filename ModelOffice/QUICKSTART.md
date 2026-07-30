# ModelOffice 快速开始

ModelOffice 是一个安全的 Python 代码执行沙箱系统。

## 5 分钟快速上手

### 1. 创建你的第一个沙箱

```bash
# 创建环境
mtb office env create my-env

# 查看环境列表
mtb office env list
```

### 2. 安装依赖包

```bash
# 安装单个包
mtb office env install my-env requests

# 安装多个包
mtb office env install my-env numpy pandas matplotlib

# 查看已安装的包
mtb office env packages my-env
```

### 3. 执行代码

#### 方法 1: 直接执行命令

```bash
mtb office exec my-env python -c "print('Hello, ModelOffice!')"
```

#### 方法 2: 执行脚本文件

```bash
# 创建测试脚本
echo "import requests; print(requests.get('https://httpbin.org/get').status_code)" > test.py

# 上传脚本
mtb office upload my-env test.py workspace/test.py

# 执行脚本
mtb office exec my-env python workspace/test.py

# 下载结果（如果有输出文件）
mtb office download my-env workspace/output.txt result.txt
```

### 4. 使用 Python API

```python
from modeltoolbox_office import Sandbox

# 创建沙箱
sandbox = Sandbox.create("demo")

# 安装包
sandbox.install(["requests", "beautifulsoup4"])

# 上传代码
sandbox.upload("script.py", "workspace/script.py")

# 执行代码
result = sandbox.execute("python workspace/script.py")
print(result["stdout"])
print(f"Exit code: {result['exit_code']}")

# 下载结果
sandbox.download("workspace/output.json", "result.json")

# 清理
sandbox.destroy()
```

## 常见使用场景

### 场景 1: 用户提交代码执行

```python
from modeltoolbox_office import Sandbox

def execute_user_code(user_id: str, code: str) -> dict:
    """执行用户提交的代码"""
    # 为每个用户创建独立环境
    env_name = f"user-{user_id}"
    sandbox = Sandbox.create(env_name)
    
    try:
        # 上传代码
        sandbox.upload_text(code, "workspace/script.py")
        
        # 执行（30秒超时，禁止网络）
        result = sandbox.execute(
            "python workspace/script.py",
            timeout=30,
            network=False
        )
        
        return {
            "success": result["exit_code"] == 0,
            "output": result["stdout"],
            "error": result["stderr"]
        }
    finally:
        sandbox.destroy()
```

### 场景 2: AI Agent 代码验证

```python
from modeltoolbox_office import Sandbox

def ai_coding_loop(task: str):
    """AI 生成代码并验证"""
    sandbox = Sandbox.create("ai-workspace")
    
    # 安装常用库
    sandbox.install(["numpy", "pandas"])
    
    while True:
        # AI 生成代码
        code = ai_generate_code(task)
        
        # 在沙箱中验证
        sandbox.upload_text(code, "workspace/solution.py")
        result = sandbox.execute("python workspace/solution.py")
        
        if result["exit_code"] == 0:
            print("✅ 代码执行成功！")
            break
        else:
            print(f"❌ 错误: {result['stderr']}")
            # 将错误反馈给 AI
            task += f"\n错误: {result['stderr']}"
    
    sandbox.destroy()
```

### 场景 3: 快照和回滚

```bash
# 创建干净环境
mtb office env create dev-env
mtb office env install dev-env requests numpy

# 创建检查点
mtb office snapshot create dev-env checkpoint-1

# 实验性修改
mtb office env install dev-env experimental-package

# 出错后回滚
mtb office snapshot restore dev-env checkpoint-1
```

### 场景 4: 环境克隆

```bash
# 创建模板环境
mtb office env create template
mtb office env install template requests pandas numpy matplotlib

# 为每个用户克隆
mtb office env clone template user-alice
mtb office env clone template user-bob
mtb office env clone template user-charlie

# 用户独立工作，互不干扰
```

## 安全特性

### 执行超时

```bash
# 设置 60 秒超时
mtb office exec my-env python long_script.py --timeout 60
```

### 网络隔离

```bash
# 禁止网络访问
mtb office exec my-env python script.py --no-network

# 允许网络访问（默认）
mtb office exec my-env python script.py --network
```

### 文件系统隔离

- 代码只能访问 `workspace/` 目录
- 无法访问系统文件和其他用户的文件
- 路径验证防止目录遍历攻击

### 审计日志

```bash
# 查看所有执行记录
mtb office audit

# 查看特定环境的记录
mtb office audit --env my-env

# 查看最近 10 条记录
mtb office audit --limit 10
```

## 清理和维护

```bash
# 清理工作区（保留已安装的包）
mtb office clean my-env --keep-packages

# 完全清理工作区
mtb office clean my-env

# 销毁环境
mtb office env destroy my-env

# 强制销毁（跳过确认）
mtb office env destroy my-env --force
```

## 故障排除

### 问题 1: 包安装失败

```bash
# 检查网络连接
mtb office exec my-env python -c "import urllib.request; print(urllib.request.urlopen('https://pypi.org').status)"

# 使用国内镜像
mtb office exec my-env pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package-name
```

### 问题 2: 脚本执行超时

```bash
# 增加超时时间
mtb office exec my-env python script.py --timeout 300
```

### 问题 3: 环境损坏

```bash
# 销毁并重建
mtb office env destroy my-env
mtb office env create my-env
```

## 更多资源

- 📄 [完整文档](README.md)
- 📋 [功能规格](../docs/SPEC_ModelOffice_v1.md)
- ✅ [重构报告](REFACTOR_COMPLETE.md)
- 🧪 [测试用例](tests/test_office.py)
- 🎬 [演示脚本](demo.py)

## 下一步

1. 阅读完整的 [README.md](README.md)
2. 查看 [API 文档](../docs/SPEC_ModelOffice_v1.md#71-python-api)
3. 运行演示脚本: `python demo.py`
4. 运行测试套件: `pytest tests/`

---

**开始使用**: `mtb office env create my-first-env` 🚀
