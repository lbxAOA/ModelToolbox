"""测试 ModelCore 的核心功能"""
import pytest
import sqlite3
from pathlib import Path
from modeltoolbox_core.config import get_state_dir
from modeltoolbox_core.paths import resolve_in_root, safe_rmtree
from modeltoolbox_core.proc import run_command
from modeltoolbox_core.store import get_db
from modeltoolbox_core.git_guard import inspect_git_deletions


def test_get_state_dir(tmp_path, monkeypatch):
    """测试状态目录获取"""
    # 使用临时目录
    monkeypatch.setenv("MODELTOOLBOX_STATE", str(tmp_path))
    
    state_dir = get_state_dir()
    assert state_dir == tmp_path
    assert state_dir.exists()


def test_resolve_in_root_safe(tmp_path):
    """测试路径解析 - 安全情况"""
    root = tmp_path / "workspace"
    root.mkdir()
    
    target = root / "subdir" / "file.txt"
    resolved = resolve_in_root(root, target)
    
    assert resolved.is_relative_to(root)


def test_resolve_in_root_traversal(tmp_path):
    """测试路径解析 - 防止路径遍历"""
    root = tmp_path / "workspace"
    root.mkdir()
    
    # 尝试逃逸
    dangerous = root / ".." / ".." / "etc" / "passwd"
    
    with pytest.raises(ValueError, match="Path traversal"):
        resolve_in_root(root, dangerous)


def test_safe_rmtree(tmp_path):
    """测试安全删除目录"""
    target = tmp_path / "to_delete"
    target.mkdir()
    
    # 创建几个文件
    for i in range(3):
        (target / f"file{i}.txt").write_text(f"content {i}")
    
    safe_rmtree(target, max_files=10)
    
    assert not target.exists()


def test_safe_rmtree_too_many_files(tmp_path):
    """测试安全删除 - 文件数超限"""
    target = tmp_path / "many_files"
    target.mkdir()
    
    # 创建超过限制的文件
    for i in range(15):
        (target / f"file{i}.txt").write_text("data")
    
    with pytest.raises(ValueError, match="Too many files"):
        safe_rmtree(target, max_files=10)


def test_run_command_success():
    """测试命令执行 - 成功"""
    result = run_command(
        ["python", "-c", "print('hello')"],
        timeout=5.0,
    )
    
    assert result.returncode == 0
    assert "hello" in result.stdout
    assert result.duration > 0


def test_run_command_failure():
    """测试命令执行 - 失败"""
    result = run_command(
        ["python", "-c", "import sys; sys.exit(1)"],
        timeout=5.0,
    )
    
    assert result.returncode == 1


def test_run_command_timeout():
    """测试命令执行 - 超时"""
    with pytest.raises(TimeoutError):
        run_command(
            ["python", "-c", "import time; time.sleep(10)"],
            timeout=0.5,
        )


def test_get_db_basic(tmp_path):
    """测试 SQLite 数据库辅助函数"""
    db_path = tmp_path / "test.db"
    
    with get_db(db_path) as conn:
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
        conn.execute("INSERT INTO test (value) VALUES (?)", ("hello",))
    
    # 验证数据已保存
    with get_db(db_path, wal=False) as conn:
        cursor = conn.execute("SELECT value FROM test")
        row = cursor.fetchone()
        assert row[0] == "hello"


def test_get_db_wal_mode(tmp_path):
    """测试 WAL 模式启用"""
    db_path = tmp_path / "test_wal.db"
    
    with get_db(db_path, wal=True) as conn:
        cursor = conn.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        assert mode.upper() == "WAL"


def test_git_deletions_within_limit(tmp_path):
    """测试 Git 删除检查 - 在限制内"""
    # 创建一个临时 git 仓库
    repo = tmp_path / "repo"
    repo.mkdir()
    
    run_command(["git", "init"], cwd=repo)
    run_command(["git", "config", "user.email", "test@test.com"], cwd=repo)
    run_command(["git", "config", "user.name", "Test"], cwd=repo)
    
    # 创建并提交一些文件
    for i in range(3):
        (repo / f"file{i}.txt").write_text(f"content {i}")
    
    run_command(["git", "add", "."], cwd=repo)
    run_command(["git", "commit", "-m", "Initial"], cwd=repo)
    
    # 删除 2 个文件
    (repo / "file0.txt").unlink()
    (repo / "file1.txt").unlink()
    run_command(["git", "add", "."], cwd=repo)
    
    # 检查删除
    report = inspect_git_deletions(repo, max_deleted=5)
    
    assert report.deleted_count == 2
    assert report.allowed is True
    assert len(report.deleted_paths) == 2


def test_git_deletions_exceeds_limit(tmp_path):
    """测试 Git 删除检查 - 超过限制"""
    repo = tmp_path / "repo"
    repo.mkdir()
    
    run_command(["git", "init"], cwd=repo)
    run_command(["git", "config", "user.email", "test@test.com"], cwd=repo)
    run_command(["git", "config", "user.name", "Test"], cwd=repo)
    
    # 创建并提交文件
    for i in range(10):
        (repo / f"file{i}.txt").write_text(f"content {i}")
    
    run_command(["git", "add", "."], cwd=repo)
    run_command(["git", "commit", "-m", "Initial"], cwd=repo)
    
    # 删除 8 个文件
    for i in range(8):
        (repo / f"file{i}.txt").unlink()
    
    run_command(["git", "add", "."], cwd=repo)
    
    # 检查删除
    report = inspect_git_deletions(repo, max_deleted=5)
    
    assert report.deleted_count == 8
    assert report.allowed is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
