import requests
from flask import Blueprint, send_file, jsonify, request
from urllib.parse import unquote
import io
from werkzeug.utils import secure_filename
import logging

# ��建蓝图
proxy_bp = Blueprint('proxy', __name__)
logger = logging.getLogger(__name__)

@proxy_bp.route('/api/proxy/image')
def proxy_image():
    """代理外部图片请求，解决CORS问题"""
    try:
        image_url = unquote(request.args.get('url', ''))
        if not image_url:
            return jsonify({'error': 'Missing URL parameter'}), 400

        logger.info(f"Proxying image request: {image_url}")

        # 设置请求头，模拟浏览器请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://maas-log-prod.cn-wlcb.ufileos.com/',
        }

        # 添加重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 发起图片请求，使用流式下载以节省内存
                response = requests.get(image_url, headers=headers, timeout=15, stream=True)
                response.raise_for_status()
                break
            except requests.exceptions.Timeout:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Timeout on attempt {attempt + 1}, retrying...")
                continue
            except requests.exceptions.ConnectionError as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Connection error on attempt {attempt + 1}, retrying...")
                continue
        else:
            raise Exception("Failed to fetch image after retries")

        # 获取内容类型
        content_type = response.headers.get('content-type', 'image/jpeg')
        content_length = response.headers.get('content-length')

        logger.info(f"Successfully fetched image: {content_type}, size: {content_length}")

        # 设置缓存头
        cache_headers = {
            'Cache-Control': 'public, max-age=3600',  # 缓存1小时
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
        }

        # 创建生成器函数用于流式传输
        def generate():
            try:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # 过滤掉保持连接的新块
                        yield chunk
            except Exception as e:
                logger.error(f"Error streaming image: {str(e)}")
                raise
            finally:
                response.close()

        # 返回流式响应
        from flask import Response
        return Response(
            generate(),
            mimetype=content_type,
            headers=cache_headers
        )

    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching image {image_url}")
        return jsonify({'error': 'Request timeout - the image server is not responding'}), 504
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error fetching image {image_url}: {str(e)}")
        return jsonify({'error': f'Connection failed - unable to reach image server'}), 502
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else 500
        logger.error(f"HTTP error {status_code} fetching image {image_url}: {str(e)}")
        return jsonify({'error': f'HTTP error {status_code} - image may not exist or be accessible'}), status_code
    except Exception as e:
        logger.error(f"Unexpected error in image proxy: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@proxy_bp.route('/api/proxy/image/download')
def proxy_image_download():
    """代理外部图片下载，提供文件名和正确的下载头"""
    try:
        image_url = unquote(request.args.get('url', ''))
        if not image_url:
            return jsonify({'error': 'Missing URL parameter'}), 400

        # 从URL提取文件名
        import re
        filename_match = re.search(r'/([^/?]+)(?:\?.*)?$', image_url)
        filename = filename_match.group(1) if filename_match else 'image.png'
        filename = secure_filename(filename)
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            filename += '.png'

        logger.info(f"Proxying image download: {image_url} as {filename}")

        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Referer': 'https://maas-log-prod.cn-wlcb.ufileos.com/',
        }

        # 下载图片
        response = requests.get(image_url, headers=headers, timeout=15)
        response.raise_for_status()

        # 获取内容类型
        content_type = response.headers.get('content-type', 'image/jpeg')

        return send_file(
            io.BytesIO(response.content),
            mimetype=content_type,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f"Error in image download proxy: {str(e)}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500