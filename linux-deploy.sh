#!/bin/bash

################################################################################
# MaynorAI Banana Pro Slides - Linux 一键部署脚本
# 适用于: Ubuntu 20.04+, Debian 11+, CentOS 8+, RHEL 8+
################################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║     🍌 MaynorAI Banana Pro Slides - Linux 部署脚本 🍌        ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测操作系统
detect_os() {
    print_info "检测操作系统..."

    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        OS_VERSION=$VERSION_ID
        print_success "检测到系统: $PRETTY_NAME"
    else
        print_error "无法检测操作系统"
        exit 1
    fi
}

# 检查是否为 root 用户
check_root() {
    if [ "$EUID" -eq 0 ]; then
        IS_ROOT=true
        SUDO=""
    else
        IS_ROOT=false
        SUDO="sudo"
        print_warning "非 root 用户，将使用 sudo"
    fi
}

# 安装 Docker
install_docker() {
    print_info "检查 Docker 安装状态..."

    if command -v docker &> /dev/null; then
        print_success "Docker 已安装: $(docker --version)"
        return 0
    fi

    print_info "开始安装 Docker..."

    case $OS in
        ubuntu|debian)
            # Ubuntu/Debian
            $SUDO apt-get update
            $SUDO apt-get install -y \
                apt-transport-https \
                ca-certificates \
                curl \
                gnupg \
                lsb-release

            # 添加 Docker 官方 GPG key
            curl -fsSL https://download.docker.com/linux/$OS/gpg | $SUDO gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

            # 添加 Docker 仓库
            echo \
                "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/$OS \
                $(lsb_release -cs) stable" | $SUDO tee /etc/apt/sources.list.d/docker.list > /dev/null

            # 安装 Docker
            $SUDO apt-get update
            $SUDO apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;

        centos|rhel|rocky|alma)
            # CentOS/RHEL
            $SUDO yum install -y yum-utils
            $SUDO yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            $SUDO yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            $SUDO systemctl start docker
            $SUDO systemctl enable docker
            ;;

        *)
            print_error "不支持的操作系统: $OS"
            print_info "请手动安装 Docker: https://docs.docker.com/engine/install/"
            exit 1
            ;;
    esac

    # 将当前用户添加到 docker 组
    if [ "$IS_ROOT" = false ]; then
        print_info "将当前用户添加到 docker 组..."
        $SUDO usermod -aG docker $USER
        print_warning "需要重新登录才能使用 docker 命令（无需 sudo）"
    fi

    print_success "Docker 安装完成: $(docker --version)"
}

# 安装 Git
install_git() {
    print_info "检查 Git 安装状态..."

    if command -v git &> /dev/null; then
        print_success "Git 已安装: $(git --version)"
        return 0
    fi

    print_info "安装 Git..."

    case $OS in
        ubuntu|debian)
            $SUDO apt-get update
            $SUDO apt-get install -y git
            ;;
        centos|rhel|rocky|alma)
            $SUDO yum install -y git
            ;;
        *)
            print_error "无法自动安装 Git"
            exit 1
            ;;
    esac

    print_success "Git 安装完成: $(git --version)"
}

# 克隆项目
clone_project() {
    print_info "准备克隆项目..."

    # 询问 Git 仓库 URL
    echo ""
    echo -e "${YELLOW}请输入 Git 仓库地址（例如: https://github.com/username/banana-slides.git）${NC}"
    echo -n "仓库地址: "
    read -r REPO_URL

    if [ -z "$REPO_URL" ]; then
        print_error "仓库地址不能为空"
        exit 1
    fi

    # 询问安装目录
    echo ""
    echo -e "${YELLOW}请输入安装目录（默认: /opt/banana-slides）${NC}"
    echo -n "安装目录: "
    read -r INSTALL_DIR

    INSTALL_DIR=${INSTALL_DIR:-/opt/banana-slides}

    # 检查目录是否存在
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "目录已存在: $INSTALL_DIR"
        echo -n "是否删除并重新克隆？ (y/N): "
        read -r CONFIRM
        if [[ $CONFIRM =~ ^[Yy]$ ]]; then
            $SUDO rm -rf "$INSTALL_DIR"
        else
            print_info "使用现有目录"
            cd "$INSTALL_DIR"
            return 0
        fi
    fi

    # 克隆项目
    print_info "克隆项目到: $INSTALL_DIR"
    $SUDO git clone "$REPO_URL" "$INSTALL_DIR"

    # 设置权限
    $SUDO chown -R $USER:$USER "$INSTALL_DIR"

    cd "$INSTALL_DIR"
    print_success "项目克隆完成"
}

# 配置环境变量
configure_env() {
    print_info "配置环境变量..."

    if [ -f .env ]; then
        print_warning ".env 文件已存在"
        echo -n "是否重新配置？ (y/N): "
        read -r CONFIRM
        if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
            print_info "使用现有 .env 配置"
            return 0
        fi
        mv .env .env.backup.$(date +%Y%m%d_%H%M%S)
    fi

    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}           API 配置向导${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════${NC}"
    echo ""

    # 文本生成 API
    echo -e "${BLUE}1. 文本生成 API 配置（用于生成大纲和描述）${NC}"
    echo -n "   Google API Key: "
    read -r TEXT_API_KEY
    echo -n "   API Base URL (默认: https://generativelanguage.googleapis.com): "
    read -r TEXT_API_BASE
    TEXT_API_BASE=${TEXT_API_BASE:-https://generativelanguage.googleapis.com}

    echo ""
    echo -e "${BLUE}2. 图片生成 API 配置${NC}"
    echo -n "   Image API Key: "
    read -r IMAGE_API_KEY
    echo -n "   API Base URL (默认: https://apipro.maynor1024.live): "
    read -r IMAGE_API_BASE
    IMAGE_API_BASE=${IMAGE_API_BASE:-https://apipro.maynor1024.live}

    echo ""
    echo -e "${BLUE}3. 服务器配置${NC}"
    echo -n "   后端端口 (默认: 5000): "
    read -r BACKEND_PORT
    BACKEND_PORT=${BACKEND_PORT:-5000}

    echo -n "   前端端口 (默认: 3000): "
    read -r FRONTEND_PORT
    FRONTEND_PORT=${FRONTEND_PORT:-3000}

    # 生成 .env 文件
    cat > .env << EOF
# Google Gemini API 配置（支持分别配置文本和图片生成）
# 文本生成（gemini-2.5-flash）
GOOGLE_API_KEY=$TEXT_API_KEY
GOOGLE_API_BASE=$TEXT_API_BASE

# 图片生成（gemini-3-pro-image-preview）
GOOGLE_IMAGE_API_KEY=$IMAGE_API_KEY
GOOGLE_IMAGE_API_BASE=$IMAGE_API_BASE

# 内置默认密钥（用于"内置配置"预设）
DEFAULT_TEXT_API_KEY=$TEXT_API_KEY
DEFAULT_IMAGE_API_KEY=$IMAGE_API_KEY

# Flask 配置
LOG_LEVEL=INFO
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
PORT=$BACKEND_PORT

# CORS 配置
CORS_ORIGINS=*

# 并发配置
MAX_DESCRIPTION_WORKERS=2
MAX_IMAGE_WORKERS=3

# MinerU 配置（可选）
MINERU_TOKEN=
MINERU_API_BASE=https://mineru.net

# 图片识别模型
IMAGE_CAPTION_MODEL=gemini-2.5-flash
EOF

    # 修改 docker-compose.yml 中的前端端口
    if [ "$FRONTEND_PORT" != "3000" ]; then
        sed -i "s/\"3000:80\"/\"$FRONTEND_PORT:80\"/" docker-compose.yml
    fi

    print_success ".env 文件已创建"
    print_info "后端端口: $BACKEND_PORT"
    print_info "前端端口: $FRONTEND_PORT"
}

# 启动服务
start_services() {
    print_info "启动 Docker 服务..."

    # 停止现有服务
    docker compose down 2>/dev/null || true

    # 构建并启动
    print_info "构建 Docker 镜像（首次运行可能需要几分钟）..."
    docker compose build --no-cache

    print_info "启动服务..."
    docker compose up -d

    # 等待服务启动
    print_info "等待服务启动..."
    sleep 10

    # 检查服务状态
    docker compose ps

    print_success "服务已启动"
}

# 检查服务健康状态
check_health() {
    print_info "检查服务健康状态..."

    # 读取端口配置
    BACKEND_PORT=$(grep "^PORT=" .env | cut -d'=' -f2)
    BACKEND_PORT=${BACKEND_PORT:-5000}

    FRONTEND_PORT=$(grep -A 2 "frontend:" docker-compose.yml | grep "ports:" -A 1 | tail -1 | sed 's/.*"\([0-9]*\):.*/\1/')
    FRONTEND_PORT=${FRONTEND_PORT:-3000}

    # 检查后端
    sleep 5
    if curl -sf http://localhost:$BACKEND_PORT/health > /dev/null; then
        print_success "后端服务运行正常: http://localhost:$BACKEND_PORT"
    else
        print_error "后端服务健康检查失败"
        docker compose logs backend
    fi

    # 检查前端
    if curl -sf http://localhost:$FRONTEND_PORT > /dev/null; then
        print_success "前端服务运行正常: http://localhost:$FRONTEND_PORT"
    else
        print_warning "前端服务可能还在启动中..."
    fi
}

# 显示访问信息
show_access_info() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    🎉 部署成功！ 🎉                           ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # 获取服务器 IP
    SERVER_IP=$(hostname -I | awk '{print $1}')

    BACKEND_PORT=$(grep "^PORT=" .env | cut -d'=' -f2)
    BACKEND_PORT=${BACKEND_PORT:-5000}

    FRONTEND_PORT=$(grep -A 2 "frontend:" docker-compose.yml | grep "ports:" -A 1 | tail -1 | sed 's/.*"\([0-9]*\):.*/\1/')
    FRONTEND_PORT=${FRONTEND_PORT:-3000}

    echo -e "${BLUE}📱 访问地址:${NC}"
    echo -e "   前端界面: ${GREEN}http://localhost:$FRONTEND_PORT${NC}"
    echo -e "   前端界面: ${GREEN}http://$SERVER_IP:$FRONTEND_PORT${NC}"
    echo ""
    echo -e "${BLUE}🔧 后端 API:${NC}"
    echo -e "   API 地址: ${GREEN}http://localhost:$BACKEND_PORT${NC}"
    echo -e "   健康检查: ${GREEN}http://localhost:$BACKEND_PORT/health${NC}"
    echo ""
    echo -e "${BLUE}🐳 Docker 管理:${NC}"
    echo -e "   查看日志: ${YELLOW}docker compose logs -f${NC}"
    echo -e "   查看状态: ${YELLOW}docker compose ps${NC}"
    echo -e "   停止服务: ${YELLOW}docker compose stop${NC}"
    echo -e "   重启服务: ${YELLOW}docker compose restart${NC}"
    echo -e "   删除服务: ${YELLOW}docker compose down${NC}"
    echo ""
    echo -e "${BLUE}📂 项目目录:${NC}"
    echo -e "   ${GREEN}$INSTALL_DIR${NC}"
    echo ""
    echo -e "${BLUE}📝 配置文件:${NC}"
    echo -e "   环境变量: ${GREEN}$INSTALL_DIR/.env${NC}"
    echo -e "   Docker: ${GREEN}$INSTALL_DIR/docker-compose.yml${NC}"
    echo ""

    if [ "$IS_ROOT" = false ] && ! groups $USER | grep -q docker; then
        echo -e "${YELLOW}⚠️  提示: 需要重新登录才能无需 sudo 使用 docker 命令${NC}"
        echo ""
    fi
}

# 主函数
main() {
    print_header

    # 检测系统
    detect_os
    check_root

    # 安装依赖
    install_git
    install_docker

    # 克隆项目
    clone_project

    # 配置环境
    configure_env

    # 启动服务
    start_services

    # 检查健康
    check_health

    # 显示访问信息
    show_access_info

    print_success "部署完成！"
}

# 运行主函数
main "$@"
