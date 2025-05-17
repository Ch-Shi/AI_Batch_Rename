import requests
import time
from config import API_URL, API_KEY, MODEL, DEFAULT_PROMPT, MAX_RETRIES
from utils.logger import logger

def get_image_caption(image_data_uri):
    """
    调用硅基流动 API 的多模态对话接口，获取给定图像的名称描述。
    参数 image_data_uri: 图像数据的 base64 data URI 字符串。
    返回模型生成的简短名称（字符串）。请求或解析失败则抛出异常。
    """
    # 构造请求消息内容：包含图像（base64 URI）和文本提示
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_data_uri,
                        "detail": "low"
                    }
                },
                {
                    "type": "text",
                    "text": DEFAULT_PROMPT
                }
            ]
        }
    ]
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    # 尝试发送请求，失败则按配置重试
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # 添加请求间隔，使用指数退避策略
            if attempt > 1:
                wait_time = 2 ** (attempt - 1)  # 2, 4, 8 秒
                logger.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        except Exception as e:
            logger.warning(f"第{attempt}次请求异常: {e}")
            if attempt == MAX_RETRIES:
                raise RuntimeError("API 请求失败，已达到最大重试次数")
            continue
        # 检查HTTP响应状态
        if response.status_code == 200:
            data = response.json()
            try:
                # 提取模型回答内容
                result_text = data["choices"][0]["message"]["content"]
            except Exception as e:
                raise RuntimeError(f"API 返回格式异常: {data}")
            # 返回去除首尾空白的名称字符串
            return result_text.strip()
        else:
            logger.warning(f"第{attempt}次请求失败: HTTP {response.status_code} - {response.text}")
            if attempt == MAX_RETRIES:
                raise RuntimeError(f"API 请求失败，状态码: {response.status_code}")
    # 正常情况下不会执行到此处
