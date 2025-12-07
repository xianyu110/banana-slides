"""
添加用户模板脚本（简化版）
直接操作数据库和文件系统
"""
import os
import sys
import uuid
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime

def add_templates():
    """添加模板"""
    # 项目根目录
    project_root = Path(__file__).parent

    # 源图片目录
    img_dir = project_root / 'img'

    # 上传目录
    upload_folder = project_root / 'uploads'
    user_templates_dir = upload_folder / 'user-templates'
    user_templates_dir.mkdir(parents=True, exist_ok=True)

    # 数据库路径
    db_path = project_root / 'backend' / 'instance' / 'database.db'

    # 模板名称映射
    template_names = {
        '13f7b8f1f5858efaf6d91c09cf0f98dd.jpg': '简约商务风格',
        '22aabcfcfa8a0dcb152376cc749baa4f.jpg': '现代科技风格',
        'd2138e0b6e15d2f0261be6772c13f7d5.jpg': '创意设计风格'
    }

    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 检查表是否存在
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='user_templates'
    """)

    if not cursor.fetchone():
        print("创建 user_templates 表...")
        cursor.execute("""
            CREATE TABLE user_templates (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(200),
                file_path VARCHAR(500) NOT NULL,
                file_size INTEGER,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
        """)
        conn.commit()

    # 处理每个图片
    for img_file in sorted(img_dir.glob('*.jpg')):
        print(f"\n处理图片: {img_file.name}")

        # 生成模板 ID
        template_id = str(uuid.uuid4())

        # 创建模板目录
        template_dir = user_templates_dir / template_id
        template_dir.mkdir(parents=True, exist_ok=True)

        # 复制文件
        dest_file = template_dir / img_file.name
        shutil.copy2(img_file, dest_file)
        print(f"  ✓ 文件已复制到: {dest_file}")

        # 获取文件大小
        file_size = img_file.stat().st_size

        # 获取模板名称
        template_name = template_names.get(img_file.name, img_file.stem)

        # 相对路径
        relative_path = f"user-templates/{template_id}/{img_file.name}"

        # 当前时间
        now = datetime.utcnow().isoformat()

        # 插入数据库
        cursor.execute("""
            INSERT INTO user_templates (id, name, file_path, file_size, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (template_id, template_name, relative_path, file_size, now, now))

        print(f"  ✓ 模板名称: {template_name}")
        print(f"  ✓ 模板ID: {template_id}")
        print(f"  ✓ 文件大小: {file_size:,} 字节 ({file_size / 1024:.1f} KB)")

    # 提交到数据库
    conn.commit()
    print("\n✅ 所有模板添加成功！")

    # 显示所有模板
    cursor.execute("SELECT id, name, file_size FROM user_templates ORDER BY created_at DESC")
    templates = cursor.fetchall()
    print(f"\n📋 当前共有 {len(templates)} 个用户模板：")
    for template_id, name, size in templates:
        print(f"  • {name or '未命名'} (ID: {template_id[:8]}..., {size / 1024:.1f} KB)")

    conn.close()

if __name__ == '__main__':
    try:
        add_templates()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
