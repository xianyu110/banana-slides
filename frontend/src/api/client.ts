import axios from 'axios';

// API基础URL配置
// 开发环境：使用Vite proxy转发到本地后端
// 生产环境：使用环境变量指定的后端API地址
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

// 创建 axios 实例
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 600000, // 10分钟超时（AI生成和文件解析可能很慢）
});

// 文件上传专用的 axios 实例（更长的超时时间）
export const fileUploadClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 660000, // 11分钟超时（文件解析需要更长时间）
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 如果请求体是 FormData，删除 Content-Type 让浏览器自动设置
    // 浏览器会自动添加正确的 Content-Type 和 boundary
    if (config.data instanceof FormData) {
      // 不设置 Content-Type，让浏览器自动处理
      if (config.headers) {
        delete config.headers['Content-Type'];
      }
    } else if (config.headers && !config.headers['Content-Type']) {
      // 对于非 FormData 请求，默认设置为 JSON
      config.headers['Content-Type'] = 'application/json';
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 文件上传客户端的请求拦截器
fileUploadClient.interceptors.request.use(
  (config) => {
    // 文件上传总是使用 FormData
    if (config.headers) {
      delete config.headers['Content-Type'];
    }

    // 添加上传进度提示
    console.log('开始上传文件，这可能需要几分钟时间...');

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 统一错误处理
    if (error.response) {
      // 服务器返回错误状态码
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // 请求已发送但没有收到响应
      console.error('Network Error:', error.request);
    } else {
      // 其他错误
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// 文件上传客户端的响应拦截器
fileUploadClient.interceptors.response.use(
  (response) => {
    console.log('文件上传和处理完成');
    return response;
  },
  (error) => {
    // 特殊处理文件上传超时
    if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
      console.error('文件处理超时！这通常是因为文件太大或内容太复杂。');
      console.error('建议：');
      console.error('1. 尝试上传较小的文件（< 10MB）');
      console.error('2. 减少PPT页数');
      console.error('3. 移除复杂的图片和动画');
    }

    if (error.response) {
      console.error('文件上传错误:', error.response.data);
    } else if (error.request) {
      console.error('网络错误:', error.request);
    } else {
      console.error('错误:', error.message);
    }
    return Promise.reject(error);
  }
);

// 图片URL处理工具
// 处理外部URL、本地文件路径等多种情况
export const getImageUrl = (path?: string, timestamp?: string | number): string => {
  if (!path) return '';

  // 如果已经是完整URL，检查是否需要代理
  if (path.startsWith('http://') || path.startsWith('https://')) {
    // 对于外部图片URL，通过后端代理来避免CORS问题
    // 编码URL以避免查询参数问题
    const encodedUrl = encodeURIComponent(path);
    return `/api/proxy/image?url=${encodedUrl}`;
  }

  // 如果是本地文件路径格式，使用完整的后端 URL
  // 本地文件路径通常是 /files/{projectId}/pages/{filename} 格式
  if (path.startsWith('/files/')) {
    // 在生产环境中，需要使用完整的后端 URL
    // 在开发环境中，API_BASE_URL 为空，会通过 Vite proxy 转发
    let url = API_BASE_URL + path;

    // 添加时间戳参数避免浏览器缓存（仅在提供时间戳时添加）
    if (timestamp) {
      const ts = typeof timestamp === 'string'
        ? new Date(timestamp).getTime()
        : timestamp;
      url += (url.includes('?') ? '&' : '?') + `v=${ts}`;
    }

    return url;
  }

  // 其他相对路径，确保以 / 开头
  let url = path.startsWith('/') ? path : '/' + path;

  // 添加时间戳参数避免浏览器缓存（仅在提供时间戳时添加）
  if (timestamp) {
    const ts = typeof timestamp === 'string'
      ? new Date(timestamp).getTime()
      : timestamp;
    url += (url.includes('?') ? '&' : '?') + `v=${ts}`;
  }

  return url;
};

export default apiClient;

