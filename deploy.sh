#!/bin/bash

# Banana Slides 快速部署脚本

set -e  # 遇到错误时退出

echo "🍌 Banana Slides 部署脚本"
echo "======================================"

# 检查部署平台
echo ""
echo "请选择部署平台："
echo "1) Vercel（推荐 - 全栈部署）"
echo "2) Cloudflare Pages（仅前端）"
echo "3) Railway（仅后端）"
echo "4) 取消"
echo ""
read -p "请输入选项 (1-4): " choice

case $choice in
  1)
    echo ""
    echo "📦 准备 Vercel 部署..."

    # 检查 Vercel CLI
    if ! command -v vercel &> /dev/null; then
        echo "❌ 未安装 Vercel CLI"
        echo "安装命令: npm install -g vercel"
        exit 1
    fi

    # 构建前端
    echo "🔨 构建前端..."
    cd frontend
    npm install
    npm run build
    cd ..

    # 部署
    echo "🚀 开始部署到 Vercel..."
    vercel --prod

    echo "✅ 部署完成！"
    ;;

  2)
    echo ""
    echo "📦 准备 Cloudflare Pages 部署..."

    # 构建前端
    echo "🔨 构建前端..."
    cd frontend
    npm install
    npm run build
    cd ..

    echo ""
    echo "✅ 前端构建完成！"
    echo "📝 下一步："
    echo "1. 访问 https://dash.cloudflare.com/"
    echo "2. 进入 Pages 部分"
    echo "3. 创建新项目并连接 Git 仓库"
    echo "4. 构建设置："
    echo "   - Build command: cd frontend && npm run build"
    echo "   - Build output: frontend/dist"
    echo ""
    echo "⚠️ 注意：后端需要单独部署到 Railway 或 Render"
    ;;

  3)
    echo ""
    echo "📦 准备 Railway 部署..."

    echo "✅ 准备完成！"
    echo "📝 下一步："
    echo "1. 访问 https://railway.app/"
    echo "2. 使用 GitHub 登录"
    echo "3. 创建新项目"
    echo "4. 从 GitHub 仓库部署"
    echo "5. Railway 会自动检测 Python 项目"
    echo "6. 在 Variables 中添加环境变量"
    ;;

  4)
    echo "取消部署"
    exit 0
    ;;

  *)
    echo "❌ 无效选项"
    exit 1
    ;;
esac

echo ""
echo "🎉 完成！"
