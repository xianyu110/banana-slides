# 🚀 Banana Pro Slides 部署指南

本项目支持多种部署方式，推荐使用 Vercel 或 Cloudflare 进行部署。

---

## 📋 目录

- [方案一：Vercel 全栈部署（推荐）](#方案一vercel-全栈部署推荐)
- [方案二：Cloudflare Pages + Workers](#方案二cloudflare-pages--workers)
- [方案三：分离部署（前端 + 后端分开）](#方案三分离部署)

---

## 方案一：Vercel 全栈部署（推荐）

Vercel 支持 Python 后端和 React 前端的一体化部署。

### 1. 前置准备

1. 注册 [Vercel](https://vercel.com/) 账号
2. 安装 Vercel CLI：
   ```bash
   npm install -g vercel
   ```

### 2. 配置环境变量

在 Vercel Dashboard 或使用 CLI 配置以下环境变量：

```bash
# 文本生成 API
GOOGLE_API_KEY=your-google-api-key
GOOGLE_API_BASE=https://generativelanguage.googleapis.com

# 图片生成 API
GOOGLE_IMAGE_API_KEY=your-image-api-key
GOOGLE_IMAGE_API_BASE=https://apipro.maynor1024.live

# 内置默认密钥
DEFAULT_TEXT_API_KEY=your-default-text-key
DEFAULT_IMAGE_API_KEY=your-default-image-key

# Flask 配置
SECRET_KEY=your-secret-key-change-this
CORS_ORIGINS=*

# MinerU 配置（可选）
MINERU_TOKEN=your-mineru-token
MINERU_API_BASE=https://mineru.net
```

### 3. 部署步骤

#### 方法 A：通过 Vercel CLI

```bash
# 1. 登录 Vercel
vercel login

# 2. 在项目根目录执行
vercel

# 3. 按照提示完成配置
# - Link to existing project? No
# - Project name: banana-slides
# - Directory: ./
# - Override settings? No

# 4. 部署生产环境
vercel --prod
```

#### 方法 B：通过 GitHub（推荐）

1. 将代码推送到 GitHub
2. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
3. 点击 "Import Project"
4. 选择你的 GitHub 仓库
5. Vercel 会自动检测配置（vercel.json）
6. 配置环境变量
7. 点击 "Deploy"

### 4. 验证部署

部署完成后，Vercel 会提供一个 URL（如 `https://banana-slides.vercel.app`）

测试端点：
- 前端：`https://your-app.vercel.app`
- 后端健康检查：`https://your-app.vercel.app/health`
- API：`https://your-app.vercel.app/api/projects`

### 5. 注意事项

#### ⚠️ Serverless 限制

Vercel Serverless Functions 有以下限制：

1. **执行时间**：
   - Hobby: 10秒
   - Pro: 60秒
   - 图片生成可能超时，建议使用 Pro 计划或考虑异步处理

2. **文件存储**：
   - Serverless 环境是临时的，文件上传需要使用外部存储
   - 建议集成 Vercel Blob、AWS S3 或 Cloudflare R2

3. **数据库**：
   - SQLite 不适合 Serverless
   - 建议使用 Vercel Postgres 或其他托管数据库

#### 💡 优化建议

**使用 Vercel Postgres 替代 SQLite：**

```bash
# 安装 Vercel Postgres
npm install @vercel/postgres

# 修改 backend/app.py 中的数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_URL')
```

**文件存储使用 Vercel Blob：**

```bash
# 安装 Vercel Blob SDK
pip install vercel-blob

# 在代码中使用
from vercel_blob import put, list

# 上传文件
blob = put('filename.png', file_data)
```

---

## 方案二：Cloudflare Pages + Workers

### 1. 前端部署（Cloudflare Pages）

#### 步骤：

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 进入 "Pages" 部分
3. 点击 "Create a project"
4. 连接 Git 仓库
5. 配置构建设置：
   ```
   Build command: cd frontend && npm run build
   Build output directory: frontend/dist
   Root directory: /
   ```
6. 添加环境变量（如果需要）
7. 点击 "Save and Deploy"

#### 自定义域名：

在 Cloudflare Pages 设置中添加自定义域名。

### 2. 后端部署（Cloudflare Workers）

⚠️ **注意**：Cloudflare Workers 不直接支持 Python。需要将后端改造为 JavaScript/TypeScript。

#### 替代方案：

**推荐方式**：后端部署到支持 Python 的平台：

- **Railway** (https://railway.app/) - 推荐
- **Render** (https://render.com/)
- **Fly.io** (https://fly.io/)
- **Heroku**

#### Railway 部署步骤：

1. 访问 [Railway](https://railway.app/)
2. 使用 GitHub 登录
3. 点击 "New Project"
4. 选择 "Deploy from GitHub repo"
5. 选择你的仓库
6. Railway 会自动检测 Python 项目
7. 添加环境变量
8. 部署完成后会获得一个 API URL

#### 配置前端连接后端：

在 Cloudflare Pages 的环境变量中添加：

```bash
VITE_API_BASE_URL=https://your-backend.railway.app
```

修改 `frontend/src/api/client.ts`：

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
```

---

## 方案三：分离部署

### 前端部署选项：

1. **Vercel**
   ```bash
   cd frontend
   vercel
   ```

2. **Netlify**
   - Build command: `npm run build`
   - Publish directory: `dist`

3. **Cloudflare Pages** （见方案二）

4. **GitHub Pages**
   ```bash
   cd frontend
   npm run build
   gh-pages -d dist
   ```

### 后端部署选项：

1. **Railway** （推荐）
   - 支持 Python
   - 自动 HTTPS
   - 免费套餐可用
   - 配置文件：自动检测

2. **Render**
   - 配置文件：
     ```yaml
     # render.yaml
     services:
       - type: web
         name: banana-slides-api
         env: python
         buildCommand: "pip install -r requirements.txt"
         startCommand: "cd backend && gunicorn app:app"
         envVars:
           - key: PYTHON_VERSION
             value: 3.10
     ```

3. **Fly.io**
   ```bash
   # 安装 flyctl
   curl -L https://fly.io/install.sh | sh

   # 登录
   flyctl auth login

   # 部署
   flyctl launch
   ```

4. **自建服务器（Docker）**
   ```bash
   # 构建
   docker build -t banana-slides .

   # 运行
   docker run -p 5000:5000 \
     -e GOOGLE_API_KEY=your-key \
     banana-slides
   ```

---

## 🔧 部署后配置

### 1. CORS 配置

如果前后端分离部署，需要在后端配置 CORS：

```python
# backend/app.py
CORS(app, origins=[
    'https://your-frontend.vercel.app',
    'https://your-frontend.pages.dev'
])
```

### 2. 数据库迁移

对于生产环境，建议使用 PostgreSQL 替代 SQLite：

```bash
# 安装 psycopg2
pip install psycopg2-binary

# 修改数据库 URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
```

### 3. 文件存储

使用对象存储服务（S3、R2、Blob）替代本地文件系统。

### 4. 环境变量管理

使用平台提供的环境变量管理功能，不要将敏感信息提交到 Git。

---

## 📊 性能优化

### 前端优化：

1. 启用 CDN 缓存
2. 压缩图片资源
3. 代码分割（已在 Vite 中配置）
4. 使用 Service Worker 缓存

### 后端优化：

1. 使用 Redis 缓存 API 响应
2. 实现 API 限流
3. 优化数据库查询
4. 使用异步任务处理长时间操作（Celery + Redis）

---

## 🆘 常见问题

### Q: Vercel 部署超时？

**A**: 图片生成可能需要较长时间：
- 升级到 Pro 计划（60秒超时）
- 或使用后台任务队列（Redis + Celery）

### Q: 数据库连接错误？

**A**: Serverless 环境不适合 SQLite：
- 使用 Vercel Postgres
- 或使用 PlanetScale、Supabase 等托管数据库

### Q: 文件上传失败？

**A**: Serverless 文件系统是临时的：
- 使用 Vercel Blob
- 或使用 Cloudflare R2、AWS S3

### Q: CORS 错误？

**A**: 检查后端 CORS 配置：
```python
CORS(app, origins=['https://your-frontend-domain.com'])
```

---

## 📝 部署清单

- [ ] 配置环境变量
- [ ] 选择数据库方案（PostgreSQL 推荐）
- [ ] 选择文件存储方案（Blob/S3/R2）
- [ ] 配置自定义域名
- [ ] 配置 HTTPS（通常自动）
- [ ] 设置 CORS 白名单
- [ ] 配置 CDN 和缓存
- [ ] 测试所有功能端点
- [ ] 监控和日志配置
- [ ] 备份策略

---

## 🔗 相关链接

- [Vercel 文档](https://vercel.com/docs)
- [Cloudflare Pages 文档](https://developers.cloudflare.com/pages/)
- [Railway 文档](https://docs.railway.app/)
- [Render 文档](https://render.com/docs)

---

## 💬 需要帮助？

如果遇到部署问题，可以：

1. 查看项目 Issues: https://github.com/your-repo/issues
2. 阅读平台官方文档
3. 加入社区讨论

祝部署顺利！🎉
