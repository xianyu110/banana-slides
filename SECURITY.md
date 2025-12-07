# 🔒 安全配置指南

## 🔑 API 密钥管理

### ⚠️ 重要提示

**永远不要将真实的 API 密钥提交到 Git 仓库！**

### 配置步骤

1. **复制环境变量模板**
   ```bash
   cp .env.example .env
   ```

2. **编辑 `.env` 文件，填入您的真实密钥**
   ```bash
   nano .env
   # 或使用你喜欢的编辑器
   vim .env
   ```

3. **填写必要的密钥**
   ```env
   # Google API Key（必须）
   GOOGLE_API_KEY=your-actual-google-api-key

   # 图片生成 API Key（必须）
   GOOGLE_IMAGE_API_KEY=your-actual-image-api-key

   # MinerU Token（可选，用于文档解析）
   MINERU_TOKEN=your-actual-mineru-token
   ```

### 获取 API 密钥

#### 1. Google Gemini API Key

**官方申请：**
- 访问：https://makersuite.google.com/app/apikey
- 或：https://aistudio.google.com/app/apikey
- 登录 Google 账号
- 点击"Create API Key"
- 复制生成的密钥

**第三方代理（可选）：**
- apipro.maynor1024.live
- api.nextaicore.com
- 其他 OpenAI 兼容的代理服务

#### 2. MinerU Token（可选）

- 访问：https://mineru.net
- 注册账号
- 获取 API Token

### 安全检查清单

- [ ] `.env` 文件已添加到 `.gitignore`
- [ ] 未将 `.env` 提交到 Git
- [ ] 使用了强密码作为 `SECRET_KEY`
- [ ] 生产环境使用了独立的 API 密钥
- [ ] 定期轮换 API 密钥
- [ ] 限制了 API 密钥的使用范围

### 验证配置

运行以下命令确保密钥未泄露：

```bash
# 检查 .env 是否在 .gitignore 中
grep "^\.env$" .gitignore

# 检查 .env 是否已被 Git 跟踪
git check-ignore .env

# 应该输出: .env
```

### 密钥泄露应对

如果不小心将密钥提交到了 Git：

1. **立即更换密钥**
   - 访问 API 提供商控制台
   - 撤销旧密钥
   - 生成新密钥

2. **清理 Git 历史**
   ```bash
   # 警告：这会改写历史，慎用！
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all

   # 强制推送
   git push origin --force --all
   ```

3. **使用 BFG 工具（推荐）**
   ```bash
   # 安装 BFG
   brew install bfg  # macOS

   # 清理密钥
   bfg --replace-text passwords.txt
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   ```

## 🛡️ 生产环境安全

### 1. 使用环境变量

**Docker：**
```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
```

**Vercel：**
- Dashboard → Settings → Environment Variables

**Railway：**
- Dashboard → Variables

### 2. 使用密钥管理服务

**AWS Secrets Manager：**
```python
import boto3

def get_secret():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='banana-slides/api-keys')
    return response['SecretString']
```

**Google Secret Manager：**
```python
from google.cloud import secretmanager

def get_secret():
    client = secretmanager.SecretManagerServiceClient()
    name = "projects/PROJECT_ID/secrets/api-key/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

### 3. 限制 CORS

生产环境应该限制 CORS：

```env
# .env (生产环境)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 4. 使用 HTTPS

确保生产环境使用 HTTPS：

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    # ...
}
```

## 📝 最佳实践

### 1. 密钥轮换

定期更换 API 密钥（建议 3-6 个月）

### 2. 最小权限原则

只授予应用必要的权限

### 3. 监控使用情况

定期检查 API 使用量，发现异常及时处理

### 4. 审计日志

记录所有 API 调用，便于追踪问题

### 5. 密钥分离

开发、测试、生产使用不同的密钥

## 🔍 安全扫描

### 检查代码中的硬编码密钥

```bash
# 使用 gitleaks
docker run -v $(pwd):/path zricethezav/gitleaks:latest detect --source="/path" -v

# 使用 truffleHog
docker run --rm -it -v $(pwd):/repo trufflesecurity/trufflehog:latest filesystem /repo
```

### GitHub Secret Scanning

GitHub 会自动扫描已知的密钥格式并发出警告

## 📞 安全问题报告

如发现安全问题，请发送邮件至：security@yourdomain.com

**请勿公开披露安全漏洞**

---

## ✅ 配置完成检查

确认以下事项：

- [ ] `.env` 文件已正确配置
- [ ] `.env` 未提交到 Git
- [ ] 生产环境使用了独立密钥
- [ ] CORS 已正确限制
- [ ] 使用了 HTTPS
- [ ] 定期检查 API 使用情况

---

**记住：安全无小事，保护好您的密钥！** 🔐
