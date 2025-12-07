# 🚀 部署指南

本项目采用**前后端分离部署**方案：
- **前端**：部署到 Vercel（静态托管）
- **后端**：部署到 Render（Flask API）

## 📋 目录

- [准备工作](#准备工作)
- [后端部署（Render）](#后端部署render)
- [前端部署（Vercel）](#前端部署vercel)
- [配置CORS](#配置cors)
- [常见问题](#常见问题)

---

## 准备工作

### 1. 注册账号

- [Render](https://render.com/) - 后端部署平台（免费套餐）
- [Vercel](https://vercel.com/) - 前端部署平台（免费套餐）

### 2. 准备API密钥

- **Gemini API密钥**：从 [Google AI Studio](https://aistudio.google.com/app/apikey) 获取
- **中转API（推荐）**：https://apipro.maynor1024.live/

### 3. Fork项目到你的GitHub

点击项目页面右上角的 `Fork` 按钮，将项目复制到你的GitHub账号下。

---

## 后端部署（Render）

### 步骤1：连接GitHub仓库

1. 登录 [Render Dashboard](https://dashboard.render.com/)
2. 点击 **New** → **Web Service**
3. 选择 **Build and deploy from a Git repository**
4. 点击 **Connect** 连接你的GitHub账号
5. 选择你Fork的 `banana-slides` 仓库

### 步骤2：配置部署

填写以下信息：

| 配置项 | 值 | 说明 |
|--------|-----|------|
| **Name** | `banana-slides-backend` | 服务名称（自定义） |
| **Region** | `Oregon (US West)` | 选择离你最近的区域 |
| **Branch** | `main` | 部署分支 |
| **Root Directory** | `.` | 项目根目录 |
| **Environment** | `Docker` | 使用Docker部署 |
| **Dockerfile Path** | `./backend/Dockerfile` | Dockerfile路径 |
| **Docker Context** | `.` | Docker上下文 |
| **Plan** | `Free` | 免费套餐 |

### 步骤3：配置环境变量

在 **Environment Variables** 部分添加以下变量：

#### 必需配置：

```env
# CORS配置（先设置为*，部署后更新）
CORS_ORIGINS=*

# 应用配置
PORT=5000
LOG_LEVEL=INFO
```

> **💡 重要提示**：
> - **API密钥现已改为前端配置**：无需在后端配置 `GOOGLE_API_KEY` 等环境变量
> - 部署完成后，在前端界面的 "⚙️ 设置" 中配置API密钥即可
> - 推荐使用中转API：https://apipro.maynor1024.live/

#### 可选的后端API配置：

如果你希望在后端预设默认API配置（不推荐），可以添加：

```env
# Gemini API配置（可选，推荐在前端配置）
GOOGLE_API_KEY=你的API密钥
GOOGLE_API_BASE=https://apipro.maynor1024.live

# 图片生成API配置（可选）
GOOGLE_IMAGE_API_KEY=你的API密钥
GOOGLE_IMAGE_API_BASE=https://apipro.maynor1024.live
```

#### 可选配置：

```env
# MinerU文件解析服务（可选）
MINERU_TOKEN=你的token
MINERU_API_BASE=https://mineru.net

# 并发配置
MAX_DESCRIPTION_WORKERS=5
MAX_IMAGE_WORKERS=8

# 默认配置
DEFAULT_ASPECT_RATIO=16:9
DEFAULT_RESOLUTION=2K
IMAGE_CAPTION_MODEL=gemini-2.5-flash
```

### 步骤4：部署

1. 点击 **Create Web Service**
2. 等待部署完成（首次部署约需5-10分钟）
3. 部署成功后，你会看到一个URL，如：`https://banana-slides-backend.onrender.com`
4. **保存这个URL**，稍后配置前端时会用到

### 步骤5：验证部署

访问：`https://你的后端URL/health`

如果返回以下内容，说明部署成功：
```json
{
  "status": "ok",
  "timestamp": "2024-xx-xx..."
}
```

---

## 前端部署（Vercel）

### 步骤1：导入项目

1. 登录 [Vercel Dashboard](https://vercel.com/dashboard)
2. 点击 **Add New** → **Project**
3. 选择你Fork的 `banana-slides` 仓库
4. 点击 **Import**

### 步骤2：配置部署

| 配置项 | 值 | 说明 |
|--------|-----|------|
| **Framework Preset** | `Vite` | 自动检测 |
| **Root Directory** | `frontend` | ⚠️ 重要：必须设置为frontend |
| **Build Command** | `npm run build` | 构建命令 |
| **Output Directory** | `dist` | 输出目录 |
| **Install Command** | `npm install` | 安装命令 |

### 步骤3：配置环境变量

在 **Environment Variables** 部分添加：

```env
VITE_API_BASE_URL=https://你的Render后端URL
```

**示例**：
```env
VITE_API_BASE_URL=https://banana-slides-backend.onrender.com
```

### 步骤4：部署

1. 点击 **Deploy**
2. 等待部署完成（约1-3分钟）
3. 部署成功后，你会看到一个URL，如：`https://banana-slides.vercel.app`

---

## 配置CORS

部署完成后，需要更新后端的CORS配置：

### 方法1：通过Render Dashboard

1. 进入Render后端服务的 **Environment** 页面
2. 找到 `CORS_ORIGINS` 变量
3. 将值从 `*` 更新为你的Vercel前端URL：
   ```
   https://banana-slides.vercel.app
   ```
4. 点击 **Save Changes**
5. 服务会自动重新部署

### 方法2：多个域名

如果需要支持多个域名（例如：自定义域名 + Vercel域名）：

```env
CORS_ORIGINS=https://banana-slides.vercel.app,https://你的自定义域名.com
```

---

## 配置API密钥

部署完成后，**必须在前端界面配置API密钥**才能使用AI功能：

### 步骤1：访问前端设置

1. 打开你部署的前端URL（如：`https://banana-slides.vercel.app`）
2. 点击右上角的 **⚙️ 设置** 按钮

### 步骤2：选择API预设

在弹出的API配置窗口中：

1. 在 "快速配置预设" 下拉框中选择 **🚀 中转API（推荐）**
2. 系统会自动填充以下配置：
   - 文本API Base: `https://apipro.maynor1024.live`
   - 图片API Base: `https://apipro.maynor1024.live`

### 步骤3：输入API密钥

1. 在 "文本生成 API" 和 "图片生成 API" 的 **API Key** 字段中输入你的密钥（格式：`sk-xxx`）
2. 两个字段可以使用相同的密钥
3. 点击 **保存配置**

✅ **配置完成！** 现在可以开始使用AI生成PPT了。

> **💡 提示**：
> - 中转API地址：https://apipro.maynor1024.live/
> - 配置保存在数据库中，无需每次访问都配置
> - 如需更换API，随时可以在设置中修改

---

## 测试部署

1. 访问你的Vercel前端URL
2. 配置API密钥（见上一节）
3. 尝试创建一个新项目
4. 测试AI生成功能
5. 测试PPT导出功能

如果一切正常，恭喜你部署成功！🎉

---

## 常见问题

### Q1: 后端显示 "Application failed to respond"

**原因**：免费套餐的Render服务在15分钟无活动后会休眠。

**解决方案**：
- 首次访问需要等待约30-60秒唤醒服务
- 使用付费套餐避免休眠
- 设置定时任务每10分钟访问一次后端保持活跃

### Q2: 前端无法连接后端

**检查清单**：
1. ✅ 检查 `VITE_API_BASE_URL` 是否正确配置
2. ✅ 检查后端的 `CORS_ORIGINS` 是否包含前端URL
3. ✅ 检查后端服务是否正常运行（访问 `/health` 端点）
4. ✅ 检查浏览器控制台是否有CORS错误

### Q3: API密钥泄露风险

**最佳实践**：
- ✅ API密钥只配置在Render后端环境变量中
- ✅ 不要在前端代码中硬编码API密钥
- ✅ 不要将 `.env` 文件提交到Git仓库
- ✅ 定期轮换API密钥

### Q4: 如何更新部署

**Render（后端）**：
- 推送代码到GitHub → Render自动检测并重新部署

**Vercel（前端）**：
- 推送代码到GitHub → Vercel自动检测并重新部署

### Q5: 免费套餐限制

**Render免费套餐**：
- ✅ 750小时/月免费运行时间
- ⚠️ 15分钟无活动后休眠
- ⚠️ 冷启动时间约30-60秒

**Vercel免费套餐**：
- ✅ 100GB带宽/月
- ✅ 无休眠问题
- ✅ 全球CDN加速

### Q6: 如何绑定自定义域名

**Vercel**：
1. 进入项目 → Settings → Domains
2. 添加你的域名
3. 按照提示配置DNS记录

**Render**：
1. 进入服务 → Settings → Custom Domain
2. 添加你的域名
3. 按照提示配置DNS记录

---

## 性能优化建议

### 1. 使用Render付费套餐

- 避免休眠问题
- 更快的响应速度
- 更多的资源配额

### 2. 优化图片加载

- 使用CDN加速
- 压缩图片文件
- 懒加载优化

### 3. 数据库优化

- 定期清理旧数据
- 考虑使用PostgreSQL替代SQLite（生产环境）

---

## 获取帮助

如果遇到问题：

1. 查看 [项目文档](../README.md)
2. 提交 [Issue](https://github.com/xianyu110/banana-slides/issues)
3. 查看Render和Vercel的官方文档

---

## 安全建议

1. ✅ 定期更新依赖包
2. ✅ 不要在公共仓库中提交敏感信息
3. ✅ 使用强密码和2FA
4. ✅ 定期轮换API密钥
5. ✅ 监控API使用量，设置配额限制

---

**祝部署顺利！** 🚀

如果本项目对你有帮助，欢迎给个Star⭐️
