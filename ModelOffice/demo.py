#!/usr/bin/env python3
"""
ModelOffice Demo - 展示所有核心功能

这个演示脚本展示了 ModelOffice 的主要功能：
1. 创建沙箱环境
2. 安装包
3. 上传文件
4. 执行代码
5. 下载结果
6. 快照管理
7. 环境克隆
8. 清理和销毁
"""

from modeltoolbox_office import Sandbox
import tempfile
import os

def demo():
    print("=" * 60)
    print("ModelOffice Demo - 安全代码执行沙箱")
    print("=" * 60)
    print()
    
    # 1. 创建沙箱
    print("1️⃣  创建沙箱环境...")
    sandbox = Sandbox.create("demo")
    print("   ✅ 环境创建成功: demo")
    print()
    
    # 2. 安装包
    print("2️⃣  安装 Python 包...")
    sandbox.install(["requests"])
    print("   ✅ 已安装: requests")
    print()
    
    # 3. 上传测试脚本
    print("3️⃣  上传测试脚本...")
    test_script = '''
import sys
import requests

print("Hello from ModelOffice sandbox!")
print(f"Python version: {sys.version}")
print(f"Arguments: {sys.argv[1:]}")

# 测试网络请求
try:
    response = requests.get("https://httpbin.org/get", timeout=5)
    print(f"HTTP request successful! Status: {response.status_code}")
except Exception as e:
    print(f"HTTP request failed: {e}")

# 写入输出文件
with open("output.txt", "w") as f:
    f.write("Demo completed successfully!\\n")
    f.write(f"Arguments: {sys.argv[1:]}\\n")

print("Script completed!")
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        script_path = f.name
    
    try:
        sandbox.upload(script_path, "test.py")
        print("   ✅ 脚本已上传")
        print()
        
        # 4. 执行代码
        print("4️⃣  执行代码...")
        result = sandbox.execute("python test.py arg1 arg2", timeout=30)
        print("   📤 输出:")
        for line in result["stdout"].strip().split('\n'):
            print(f"      {line}")
        print(f"   ✅ 退出码: {result['exit_code']}")
        print()
        
        # 5. 下载结果
        print("5️⃣  下载输出文件...")
        output_path = tempfile.mktemp(suffix='.txt')
        sandbox.download("output.txt", output_path)
        with open(output_path, 'r') as f:
            content = f.read()
        print("   📥 文件内容:")
        for line in content.strip().split('\n'):
            print(f"      {line}")
        os.unlink(output_path)
        print()
        
        # 6. 创建快照
        print("6️⃣  创建快照...")
        sandbox.snapshot("checkpoint-1")
        print("   ✅ 快照已创建: checkpoint-1")
        print()
        
        # 7. 克隆环境
        print("7️⃣  克隆环境...")
        sandbox2 = Sandbox.clone("demo", "demo-copy")
        print("   ✅ 环境已克隆: demo-copy")
        print()
        
        # 8. 测试克隆的环境
        print("8️⃣  在克隆的环境中执行代码...")
        result2 = sandbox2.execute("python test.py from-clone", timeout=30)
        print(f"   ✅ 克隆环境执行成功! 退出码: {result2['exit_code']}")
        print()
        
        # 9. 清理
        print("9️⃣  清理工作区...")
        sandbox.clean()
        print("   ✅ 工作区已清理")
        print()
        
        # 10. 销毁环境
        print("🔟 销毁环境...")
        sandbox.destroy()
        sandbox2.destroy()
        print("   ✅ 环境已销毁")
        print()
        
    finally:
        # 清理临时文件
        if os.path.exists(script_path):
            os.unlink(script_path)
    
    print("=" * 60)
    print("✨ 演示完成！")
    print("=" * 60)
    print()
    print("ModelOffice 提供:")
    print("  ✅ 安全的代码执行环境")
    print("  ✅ 完整的环境管理")
    print("  ✅ 包管理和依赖隔离")
    print("  ✅ 文件上传/下载")
    print("  ✅ 快照和恢复")
    print("  ✅ 环境克隆")
    print("  ✅ 审计日志")
    print()
    print("🚀 开始使用: from modeltoolbox_office import Sandbox")

if __name__ == "__main__":
    try:
        demo()
    except KeyboardInterrupt:
        print("\n\n❌ 演示已取消")
    except Exception as e:
        print(f"\n\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()
