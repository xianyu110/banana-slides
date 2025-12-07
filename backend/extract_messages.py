#!/usr/bin/env python3
"""
提取翻译消息脚本
"""

import subprocess
import sys
import os

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Command failed: {cmd}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Error running command: {cmd}")
        print(f"Exception: {e}")
        return False

def main():
    """主函数"""
    backend_dir = os.path.dirname(os.path.abspath(__file__))

    print("🔍 提取Python代码中的翻译消息...")

    # 1. 提取消息
    if not run_command("pybabel extract -F babel.cfg -o messages.pot .", backend_dir):
        sys.exit(1)

    print("✅ 翻译消息提取完成")

    # 2. 初始化中文翻译（如果不存在）
    zh_dir = os.path.join(backend_dir, "translations", "zh", "LC_MESSAGES")
    if not os.path.exists(zh_dir):
        print("🌏 初始化中文翻译...")
        if not run_command("pybabel init -i messages.pot -d translations -l zh", backend_dir):
            sys.exit(1)
        print("✅ 中文翻译初始化完成")
    else:
        print("🌏 更新中文翻译...")
        if not run_command("pybabel update -i messages.pot -d translations", backend_dir):
            sys.exit(1)
        print("✅ 中文翻译更新完成")

    # 3. 初始化英文翻译（如果不存在）
    en_dir = os.path.join(backend_dir, "translations", "en", "LC_MESSAGES")
    if not os.path.exists(en_dir):
        print("🌍 初始化英文翻译...")
        if not run_command("pybabel init -i messages.pot -d translations -l en", backend_dir):
            sys.exit(1)
        print("✅ 英文翻译初始化完成")
    else:
        print("🌍 更新英文翻译...")
        if not run_command("pybabel update -i messages.pot -d translations", backend_dir):
            sys.exit(1)
        print("✅ 英��翻译更新完成")

    print("\n🎉 翻译文件准备完成！")
    print("📝 翻译文件位置:")
    print(f"   - 中文: {zh_dir}/messages.po")
    print(f"   - 英文: {en_dir}/messages.po")
    print("\n💡 下一步：编辑 .po 文件添加翻译，然后运行:")
    print("   pybabel compile -d translations")

if __name__ == "__main__":
    main()