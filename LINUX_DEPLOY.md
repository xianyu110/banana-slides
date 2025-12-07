# 🐧 Linux 部署指南

MaynorAI Banana Pro Slides 在 Linux 服务器上的完整部署教程

---

## 🚀 方法一：一键自动部署（推荐）

### 快速开始

```bash
# 1. 下载部署脚本
wget https://raw.githubusercontent.com/your-repo/banana-slides/main/linux-deploy.sh

# 或使用 curl
curl -O https://raw.githubusercontent.com/your-repo/banana-slides/main/linux-deploy.sh

# 2. 添加执行权限
chmod +x linux-deploy.sh

# 3. 运行部署脚本
./linux-deploy.sh
```

### 脚本会自动完成：

1. ✅ 检测操作系统（Ubuntu/Debian/CentOS/RHEL）
2. ✅ 安装 Docker 和 Docker Compose
3. ✅ 安装 Git
4. ✅ 克隆项目代码
5. ✅ 配置环境变量（交互式向导）
6. ✅ 构建 Docker 镜像
7. ✅ 启动服务
8. ✅ 健康检查
9. ✅ 显示访问信息

### 支持的系统

- ✅ Ubuntu 20.04+
- ✅ Debian 11+
- ✅ CentOS 8+
- ✅ RHEL 8+
- ✅ Rocky Linux 8+
- ✅ AlmaLinux 8+

---

## 📋 方法二：手动部署

### 步骤 1：安装 Docker

#### Ubuntu/Debian

```bash
# 更新包索引
sudo apt-get update

# 安装依赖
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 添加 Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加 Docker 仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
docker compose version
```

#### CentOS/RHEL

```bash
# 安装依赖
sudo yum install -y yum-utils

# 添加 Docker 仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装 Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
docker compose version
```

#### 将用户添加到 docker 组（可选）

```bash
# 避免每次都使用 sudo
sudo usermod -aG docker $USER

# 重新登录使更改生效
# 或者运行：
newgrp docker
```

### 步骤 2：安装 Git

```bash
# Ubuntu/Debian
sudo apt-get install -y git

# CentOS/RHEL
sudo yum install -y git

# 验证安装
git --version
```

### 步骤 3：克隆项目

```bash
# 创建项目目录
sudo mkdir -p /opt/banana-slides
cd /opt/banana-slides

# 克隆项目（替换为你的仓库地址）
git clone https://github.com/your-username/banana-slides.git .

# 设置权限
sudo chown -R $USER:$USER /opt/banana-slides
```

### 步骤 4：配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
nano .env
```

配置以下关键参数：

```env
# 文本生成 API
GOOGLE_API_KEY=your-google-api-key
GOOGLE_API_BASE=https://generativelanguage.googleapis.com

# 图片生成 API
GOOGLE_IMAGE_API_KEY=your-image-api-key
GOOGLE_IMAGE_API_BASE=https://apipro.maynor1024.live

# 内置默认密钥
DEFAULT_TEXT_API_KEY=your-default-text-key
DEFAULT_IMAGE_API_KEY=your-default-image-key

# 后端端口
PORT=5000

# 安全密钥（生成随机密钥）
SECRET_KEY=$(openssl rand -hex 32)
```

### 步骤 5：启动服务

```bash
# 构建镜像
docker compose build

# 启动服务（后台运行）
docker compose up -d

# 查看日志
docker compose logs -f

# 查看服务状态
docker compose ps
```

### 步骤 6：验证部署

```bash
# 检查后端健康
curl http://localhost:5000/health

# 应该返回：
# {"status": "healthy"}

# 检查前端
curl -I http://localhost:3000

# 应该返回 200 OK
```

---

## 🔧 配置防火墙

### Ubuntu/Debian (UFW)

```bash
# 允许端口
sudo ufw allow 3000/tcp  # 前端
sudo ufw allow 5000/tcp  # 后端

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

### CentOS/RHEL (Firewalld)

```bash
# 允许端口
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=5000/tcp

# 重载防火墙
sudo firewall-cmd --reload

# 查看状态
sudo firewall-cmd --list-all
```

---

## 🌐 配置 Nginx 反向代理（可选）

### 安装 Nginx

```bash
# Ubuntu/Debian
sudo apt-get install -y nginx

# CentOS/RHEL
sudo yum install -y nginx
```

### 配置反向代理

创建配置文件：

```bash
sudo nano /etc/nginx/sites-available/banana-slides
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

    # 前端
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 后端 API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # 文件服务
    location /files {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # 健康检查
    location /health {
        proxy_pass http://localhost:5000;
    }
}
```

启用配置：

```bash
# Ubuntu/Debian
sudo ln -s /etc/nginx/sites-available/banana-slides /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 配置 HTTPS (Let's Encrypt)

```bash
# 安装 Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## 📊 监控和日志

### 查看 Docker 日志

```bash
# 实时查看所有日志
docker compose logs -f

# 只查看后端
docker compose logs -f backend

# 只查看前端
docker compose logs -f frontend

# 查看最近 100 行
docker compose logs --tail=100

# 查看特定时间范围
docker compose logs --since 2024-01-01T00:00:00
```

### 系统资源监控

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
df -h

# 查看内存使用
free -h

# 查看进程
htop  # 需要安装: sudo apt-get install htop
```

### 设置日志轮转

创建 `/etc/logrotate.d/banana-slides`：

```bash
/opt/banana-slides/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
```

---

## 🔄 更新部署

### 拉取最新代码

```bash
cd /opt/banana-slides

# 拉取最新代码
git pull

# 重新构建并启动
docker compose down
docker compose build --no-cache
docker compose up -d

# 查看日志
docker compose logs -f
```

### 数据库迁移（如有）

```bash
# 备份数据库
docker compose exec backend cp /app/backend/instance/database.db /app/uploads/backup-$(date +%Y%m%d).db

# 如果有新的迁移脚本
docker compose exec backend python -m flask db upgrade
```

---

## 🛡️ 安全加固

### 1. 配置 SSL/TLS

使用 Let's Encrypt 或自签名证书

### 2. 限制端口访问

```bash
# 只允许通过 Nginx 访问
sudo ufw deny 3000
sudo ufw deny 5000
sudo ufw allow 80
sudo ufw allow 443
```

### 3. 定期更新系统

```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 4. 配置自动备份

创建备份脚本 `/opt/banana-slides/backup.sh`：

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/banana-slides"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
docker compose exec backend cp /app/backend/instance/database.db /app/uploads/db-backup-$DATE.db

# 备份上传文件
tar -czf $BACKUP_DIR/uploads-$DATE.tar.gz uploads/

# 删除 7 天前的备份
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

添加到 crontab：

```bash
# 编辑 crontab
crontab -e

# 添加每天凌晨 2 点备份
0 2 * * * /opt/banana-slides/backup.sh >> /var/log/banana-backup.log 2>&1
```

---

## 🆘 故障排查

### 服务无法启动

```bash
# 检查 Docker 日志
docker compose logs

# 检查端口占用
sudo netstat -tlnp | grep :5000
sudo netstat -tlnp | grep :3000

# 检查磁盘空间
df -h

# 检查内存
free -h
```

### 前端无法访问后端

```bash
# 检查网络连接
docker compose exec frontend ping backend

# 检查环境变量
docker compose exec backend env | grep API

# 检查防火墙
sudo ufw status
sudo firewall-cmd --list-all
```

### 数据库错误

```bash
# 删除并重建数据库
docker compose down
rm backend/instance/database.db
docker compose up -d
```

---

## 📞 获取帮助

如遇问题：

1. 查看日志：`docker compose logs -f`
2. 查看文档：DOCKER_DEPLOY.md
3. 提交 Issue: GitHub Issues

---

## ✅ 部署检查清单

- [ ] Docker 已安装并运行
- [ ] Git 已安装
- [ ] 项目已克隆
- [ ] .env 已配置（API 密钥）
- [ ] 防火墙已配置
- [ ] 服务已启动：`docker compose ps`
- [ ] 健康检查通过：`curl http://localhost:5000/health`
- [ ] 前端可访问：`curl -I http://localhost:3000`
- [ ] Nginx 反向代理已配置（如需要）
- [ ] SSL 证书已配置（如需要）
- [ ] 备份脚本已设置

---

## 🎉 部署完成！

访问 http://your-server-ip:3000 开始使用 MaynorAI Banana Pro Slides！
