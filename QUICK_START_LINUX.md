# 🚀 Linux 快速部署

## 一行命令部署

```bash
bash <(curl -s https://raw.githubusercontent.com/your-repo/banana-slides/main/linux-deploy.sh)
```

## 或者下载后运行

```bash
# 方法 1: 使用 wget
wget https://raw.githubusercontent.com/your-repo/banana-slides/main/linux-deploy.sh
chmod +x linux-deploy.sh
./linux-deploy.sh

# 方法 2: 使用 curl
curl -O https://raw.githubusercontent.com/your-repo/banana-slides/main/linux-deploy.sh
chmod +x linux-deploy.sh
./linux-deploy.sh
```

## 手动部署（5 步）

```bash
# 1. 安装 Docker
curl -fsSL https://get.docker.com | sh

# 2. 克隆项目
git clone https://github.com/your-username/banana-slides.git
cd banana-slides

# 3. 配置环境变量
cp .env.example .env
nano .env  # 填入你的 API 密钥

# 4. 启动服务
docker compose up -d

# 5. 访问应用
# 前端: http://localhost:3000
# 后端: http://localhost:5000
```

## 常用命令

```bash
# 查看日志
docker compose logs -f

# 查看状态
docker compose ps

# 重启服务
docker compose restart

# 停止服务
docker compose stop

# 更新项目
git pull && docker compose up -d --build
```

## 故障排查

```bash
# 检查服务状态
docker compose ps

# 查看详细日志
docker compose logs backend
docker compose logs frontend

# 重新构建
docker compose down
docker compose build --no-cache
docker compose up -d
```

## 访问地址

- **前端**: http://服务器IP:3000
- **后端**: http://服务器IP:5000/health
- **API**: http://服务器IP:5000/api

---

完整文档：[LINUX_DEPLOY.md](LINUX_DEPLOY.md)
