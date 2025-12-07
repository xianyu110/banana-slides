#!/usr/bin/env python3
"""
迁移现有项目到系统用户
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db, User, Project
from app import create_app


def create_system_user():
    """创建系统用户"""
    app = create_app()
    with app.app_context():
        # 检查是否已存在系统用户
        system_user = User.query.filter_by(email='system@banana-slides.local').first()
        if not system_user:
            system_user = User(
                email='system@banana-slides.local',
                username='System',
                auth_provider='email',
                password_hash='system_user_hash',
                email_verified=True,
                is_active=True
            )
            db.session.add(system_user)
            db.session.commit()
            print(f"✅ Created system user: {system_user.id}")
        else:
            print(f"✅ System user already exists: {system_user.id}")

        return system_user


def migrate_projects():
    """迁移现有项目到系统用户"""
    app = create_app()
    with app.app_context():
        # 获取或创建系统用户
        system_user = create_system_user()

        # 查找没有user_id的项目
        orphaned_projects = Project.query.filter(Project.user_id.is_(None)).all()

        if not orphaned_projects:
            print("✅ No orphaned projects found")
            return

        print(f"📦 Found {len(orphaned_projects)} orphaned projects")

        # 批量更新项目
        for project in orphaned_projects:
            project.user_id = system_user.id
            print(f"  🔄 Migrated project {project.id} to system user")

        db.session.commit()
        print(f"✅ Successfully migrated {len(orphaned_projects)} projects")


def backup_existing_data():
    """备份现有数据"""
    app = create_app()
    with app.app_context():
        projects = Project.query.all()

        print(f"📊 Total projects in database: {len(projects)}")

        orphaned_count = Project.query.filter(Project.user_id.is_(None)).count()
        print(f"📊 Projects without user_id: {orphaned_count}")

        users = User.query.all()
        print(f"📊 Total users in database: {len(users)}")


def main():
    """主函数"""
    print("🚀 Starting migration of existing projects to system user...")

    try:
        # 显示当前状态
        backup_existing_data()

        # 执行迁移
        migrate_projects()

        print("✅ Migration completed successfully!")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()