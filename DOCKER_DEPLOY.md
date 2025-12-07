# 🐳 Docker 部署指南

MaynorAI Banana Pro Slides 完整 Docker 部署教程

---

## 📋 快速开始

### 一键启动（推荐）

```bash
# 1. 克隆或进入项目目录
cd banana-slides

# 2. 确保 .env 文件配置正确（已有默认配置）

# 3. 启动所有服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 访问应用
# 前端: http://localhost:3000
# 后端: http://localhost:5000
```

---

## 🛠️ 详细步骤

### 1. 前置要求

确保已安装：
- Docker (>= 20.10)
- Docker Compose (>= 2.0)

**检查安装：**
```bash
docker --version
docker-compose --version
```

**安装 Docker（如未安装）：**
- macOS: https://docs.docker.com/desktop/install/mac-install/
- Windows: https://docs.docker.com/desktop/install/windows-install/
- Linux: https://docs.docker.com/engine/install/

### 2. 配置环境变量

编辑 `.env` 文件（已有默认配置，可按需修改）：

```env
# API 密钥（必须）
GOOGLE_API_KEY=your-google-api-key
GOOGLE_IMAGE_API_KEY=your-image-api-key

# API Base URLs
GOOGLE_API_BASE=https://generativelanguage.googleapis.com
GOOGLE_IMAGE_API_BASE=https://apipro.maynor1024.live

# 后端端口（默认 5000）
PORT=5000

# 其他配置保持默认即可
```

### 3. 构建和启动

#### 方法 A：使用 docker-compose（推荐）

```bash
# 构建并启动（后台运行）
docker-compose up -d --build

# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 只查看后端日志
docker-compose logs -f backend

# 只查看前端日志
docker-compose logs -f frontend
```

#### 方法 B：分别构建

```bash
# 构建后端
docker build -f backend/Dockerfile -t banana-slides-backend .

# 构建前端
docker build -f frontend/Dockerfile -t banana-slides-frontend .

# 运行后端
docker run -d \
  --name banana-backend \
  -p 5000:5000 \
  --env-file .env \
  -v $(pwd)/backend/instance:/app/backend/instance \
  -v $(pwd)/uploads:/app/uploads \
  banana-slides-backend

# 运行前端
docker run -d \
  --name banana-frontend \
  -p 3000:80 \
  --link banana-backend:backend \
  banana-slides-frontend
```

### 4. 访问应用

- **前端界面**: http://localhost:3000
- **后端 API**: http://localhost:5000
- **健康检查**: http://localhost:5000/health
- **API 文档**: http://localhost:5000/api

### 5. 停止和重启

```bash
# 停止所有服务
docker-compose stop

# 重启所有服务
docker-compose restart

# 停止并删除容器（保留数据）
docker-compose down

# 停止并删除容器和数据卷（清空所有数据）
docker-compose down -v
```

---

## 📊 容器架构

```
┌─────────────────────────────────────┐
│         Docker Network              │
│  (banana-slides-network)            │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │   Frontend   │  │   Backend   │ │
│  │   (nginx)    │  │   (Flask)   │ │
│  │   Port: 80   │  │  Port: 5000 │ │
│  └──────┬───────┘  └──────┬──────┘ │
│         │                  │        │
└─────────┼──────────────────┼────────┘
          │                  │
          │                  │
    ┌─────▼──────┐    ┌─────▼──────┐
    │  3000:80   │    │ 5000:5000  │
    │  (宿主机)   │    │  (宿主机)   │
    └────────────┘    └────────────┘
                           │
                      ┌────▼─────┐
                      │ 数据持久化 │
                      │  Volumes  │
                      └──────────┘
                      • instance/
                      • uploads/
```

---

## 🔧 常用命令

### 容器管理

```bash
# 查看所有容器
docker-compose ps

# 查看容器详细信息
docker inspect banana-slides-backend

# 进入后端容器
docker-compose exec backend sh

# 进入前端容器
docker-compose exec frontend sh

# 重启单个服务
docker-compose restart backend
docker-compose restart frontend
```

### 日志管理

```bash
# 查看所有日志
docker-compose logs

# 实时跟踪日志
docker-compose logs -f

# 查看最近 100 行日志
docker-compose logs --tail=100

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend
```

### 数据管理

```bash
# 备份数据库
docker-compose exec backend cp /app/backend/instance/database.db /app/uploads/backup.db

# 查看上传的文件
ls -la uploads/

# 清理未使用的镜像
docker image prune

# 清理未使用的容器
docker container prune

# 清理未使用的数据卷
docker volume prune
```

---

## 🚀 生产环境部署

### 1. 使用环境变量文件

创建生产环境配置：

```bash
# 创建生产环境配置
cp .env .env.production

# 编辑生产环境配置
nano .env.production
```

使用生产环境配置启动：

```bash
docker-compose --env-file .env.production up -d
```

### 2. 使用外部数据库（推荐）

修改 `backend/app.py` 配置：

```python
# 使用 PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://user:password@postgres:5432/banana_slides'
)
```

更新 `docker-compose.yml`：

```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: banana
      POSTGRES_PASSWORD: your_secure_password
      POSTGRES_DB: banana_slides
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - banana-slides-network

  backend:
    # ... 其他配置
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://banana:your_secure_password@postgres:5432/banana_slides

volumes:
  postgres-data:
```

### 3. 使用 Nginx 反向代理

创建 `nginx/nginx.conf`：

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # 前端
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 后端 API
    location /api {
        proxy_pass http://backend:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }

    # 文件服务
    location /files {
        proxy_pass http://backend:5000;
        proxy_set_header Host $host;
    }
}
```

### 4. HTTPS 配置

使用 Let's Encrypt：

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    depends_on:
      - frontend
      - backend

  certbot:
    image: certbot/certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
```

---

## 🔍 故障排查

### 问题 1：容器启动失败

```bash
# 查看详细错误信息
docker-compose logs backend

# 检查端口占用
lsof -i :5000
lsof -i :3000

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```

### 问题 2：数据库连接错误

```bash
# 检查数据库文件
ls -la backend/instance/

# 进入容器检查
docker-compose exec backend ls -la /app/backend/instance/

# 重新初始化数据库
docker-compose exec backend rm /app/backend/instance/database.db
docker-compose restart backend
```

### 问题 3：前端无法连接后端

```bash
# 检查网络
docker network ls
docker network inspect banana-slides_banana-slides-network

# 测试后端连接
docker-compose exec frontend wget -O- http://backend:5000/health

# 检查环境变量
docker-compose exec backend env | grep API
```

### 问题 4：上传文件丢失

```bash
# 检查挂载点
docker-compose exec backend ls -la /app/uploads/

# 确保宿主机目录存在
mkdir -p uploads
chmod 755 uploads

# 重启容器
docker-compose restart backend
```

### 问题 5：内存不足

```bash
# 限制容器内存
docker-compose.yml 添加:
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

---

## 📈 性能优化

### 1. 使用多阶段构建（已配置）

前端 Dockerfile 已使用多阶段构建，最终镜像只包含必要文件。

### 2. 启用 Docker BuildKit

```bash
export DOCKER_BUILDKIT=1
docker-compose build
```

### 3. 配置镜像缓存

```bash
# 使用国内镜像源
# 编辑 /etc/docker/daemon.json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn"
  ]
}

# 重启 Docker
sudo systemctl restart docker
```

### 4. 资源限制

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## 🔐 安全建议

1. **不要将 .env 文件提交到 Git**
   ```bash
   # .gitignore 已包含
   .env
   .env.production
   ```

2. **使用 Docker Secrets（生产环境）**
   ```yaml
   secrets:
     api_key:
       file: ./secrets/api_key.txt

   services:
     backend:
       secrets:
         - api_key
   ```

3. **定期更新镜像**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

4. **限制容器权限**
   ```yaml
   services:
     backend:
       user: "1000:1000"
       read_only: true
       cap_drop:
         - ALL
   ```

---

## 📦 镜像发布

### 构建并推送到 Docker Hub

```bash
# 登录 Docker Hub
docker login

# 构建并标记镜像
docker build -f backend/Dockerfile -t maynor/banana-slides-backend:latest .
docker build -f frontend/Dockerfile -t maynor/banana-slides-frontend:latest .

# 推送到 Docker Hub
docker push maynor/banana-slides-backend:latest
docker push maynor/banana-slides-frontend:latest
```

### 使用发布的镜像

修改 `docker-compose.yml`：

```yaml
services:
  backend:
    image: maynor/banana-slides-backend:latest
    # 移除 build 配置

  frontend:
    image: maynor/banana-slides-frontend:latest
    # 移除 build 配置
```

---

## 💡 最佳实践

1. **使用 .dockerignore**
   - 已配置，排除不必要的文件

2. **健康检查**
   - 已配置，自动检测服务状态

3. **数据持久化**
   - 使用 volumes 保存数据

4. **日志管理**
   - 配置日志驱动和轮转

5. **自动重启**
   - 使用 `restart: unless-stopped`

---

## 🆘 获取帮助

如果遇到问题：

1. 查看日志：`docker-compose logs -f`
2. 检查配置：`docker-compose config`
3. 查看文档：本文件和 DEPLOYMENT.md
4. 提交 Issue: GitHub Issues

---

## 🎉 完成！

现在您的 MaynorAI Banana Pro Slides 已经通过 Docker 成功部署！

访问 http://localhost:3000 开始使用吧！
