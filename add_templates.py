"""
添加用户模板脚本
将 img 目录下的图片添加为用户模板
"""
import os
import sys
import uuid
import shutil
from pathlib import Path

# 添加项目路径到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app
from models import db
from models.user_template import UserTemplate

def add_templates():
    """添加模板"""
    app = create_app()

    with app.app_context():
        # 源图片目录
        img_dir = Path(__file__).parent / 'img'

        # 上传目录
        upload_folder = Path(app.config['UPLOAD_FOLDER'])
        user_templates_dir = upload_folder / 'user-templates'
        user_templates_dir.mkdir(parents=True, exist_ok=True)

        # 模板名称映射
        template_names = {
            '13f7b8f1f5858efaf6d91c09cf0f98dd.jpg': '简约商务风格',
            '22aabcfcfa8a0dcb152376cc749baa4f.jpg': '现代科技风格',
            'd2138e0b6e15d2f0261be6772c13f7d5.jpg': '创意设计风格'
        }

        # 处理每个图片
        for img_file in img_dir.glob('*.jpg'):
            print(f"\n处理图片: {img_file.name}")

            # 生成模板 ID
            template_id = str(uuid.uuid4())

            # 创建模板目录
            template_dir = user_templates_dir / template_id
            template_dir.mkdir(parents=True, exist_ok=True)

            # 复制文件
            dest_file = template_dir / img_file.name
            shutil.copy2(img_file, dest_file)
            print(f"  文件已复制到: {dest_file}")

            # 获取文件大小
            file_size = img_file.stat().st_size

            # 获取模板名称
            template_name = template_names.get(img_file.name, img_file.stem)

            # 创建数据库记录
            template = UserTemplate(
                id=template_id,
                name=template_name,
                file_path=str(dest_file.relative_to(upload_folder)),
                file_size=file_size
            )

            db.session.add(template)
            print(f"  模板名称: {template_name}")
            print(f"  模板ID: {template_id}")
            print(f"  文件大小: {file_size} 字节")

        # 提交到数据库
        db.session.commit()
        print("\n✅ 所有模板添加成功！")

        # 显示所有模板
        templates = UserTemplate.query.all()
        print(f"\n当前共有 {len(templates)} 个用户模板：")
        for t in templates:
            print(f"  - {t.name or '未命名'} (ID: {t.id})")

if __name__ == '__main__':
    add_templates()
