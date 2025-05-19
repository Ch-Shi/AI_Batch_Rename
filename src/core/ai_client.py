import os
import requests
import time
import json
import base64
from config import (
    USE_OLLAMA, OLLAMA_BASE_URL, OLLAMA_MODEL,
    SILICON_FLOW_API_KEY, SILICON_FLOW_API_URL, SILICON_FLOW_MODEL,
    MAX_RETRIES, INITIAL_RETRY_DELAY, MAX_RETRY_DELAY,
    MAX_OUTPUT_TOKENS, DEFAULT_PROMPT
)
from utils.logger import logger
from token_monitor import token_monitor
from typing import Optional, Dict, Any

class AIClient:
    def __init__(self, api_key: Optional[str] = None, use_ollama: bool = True):
        self.api_key = api_key or SILICON_FLOW_API_KEY
        self.use_ollama = use_ollama
        self.ollama_base_url = OLLAMA_BASE_URL
        self.silicon_flow_base_url = "https://api.siliconflow.com/v1"
        
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        分析图像内容并返回描述
        """
        try:
            if self.use_ollama:
                return self._analyze_with_ollama(image_path)
            else:
                return self._analyze_with_silicon_flow(image_path)
        except Exception as e:
            logger.error(f"图像分析失败: {str(e)}")
            raise

    def _analyze_with_ollama(self, image_path: str) -> Dict[str, Any]:
        """
        使用 Ollama 的 Qwen2.5VL-7B 模型分析图像
        """
        try:
            # 读取图像文件并转换为 base64
            with open(image_path, 'rb') as f:
                image_data = f.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # 构建请求
            url = f"{self.ollama_base_url}/api/generate"
            headers = {
                "Content-Type": "application/json"
            }
            
            # 构建提示词
            prompt = "请分析这张图片的内容，并用简短的中文描述它。描述应该简洁明了，适合作为文件名。"
            
            # 构建请求体
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "images": [base64_image],
                "stream": False,
                "num_predict": MAX_OUTPUT_TOKENS  # 限制输出 token 数量
            }
            
            # 发送请求
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            description = result.get("response", "").strip()
            
            return {
                "description": description,
                "confidence": 1.0  # Ollama 不提供置信度，默认为 1.0
            }
            
        except Exception as e:
            logger.error(f"Ollama 图像分析失败: {str(e)}")
            raise

    def _analyze_with_silicon_flow(self, image_path: str) -> Dict[str, Any]:
        """
        使用硅基流动 API 分析图像（保留原有功能）
        """
        try:
            # 读取图像文件
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # 构建请求
            url = f"{self.silicon_flow_base_url}/vision/analyze"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 构建请求体
            payload = {
                "image": image_data,
                "model": SILICON_FLOW_MODEL
            }
            
            # 发送请求
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            description = result.get("description", "")
            confidence = result.get("confidence", 0.0)
            
            return {
                "description": description,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"硅基流动图像分析失败: {str(e)}")
            raise

    def _monitor_token_usage(self, response):
        """监控 token 使用情况"""
        if not self.use_ollama:
            # 硅基流动 API 的 token 监控
            if 'usage' in response:
                usage = response['usage']
                current = usage.get('total_tokens', 0)
                remaining = self.max_tokens - current
                usage_rate = (current / self.max_tokens) * 100
                logger.info(f"Token 使用情况 - 当前: {current}, 剩余: {remaining}, 使用率: {usage_rate:.1f}%")
        else:
            # Ollama 本地服务不需要显示 token 使用情况
            pass

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
        "model": SILICON_FLOW_MODEL,
        "messages": messages,
        "stream": False,
        "max_tokens": MAX_OUTPUT_TOKENS
    }
    headers = {
        "Authorization": f"Bearer {SILICON_FLOW_API_KEY}",
        "Content-Type": "application/json"
    }
    # 尝试发送请求，失败则按配置重试
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # 添加请求间隔，使用指数退避策略，但限制最大延迟
            if attempt > 1:
                wait_time = min(INITIAL_RETRY_DELAY * (2 ** (attempt - 2)), MAX_RETRY_DELAY)
                logger.info(f"等待 {wait_time:.1f} 秒后重试...")
                time.sleep(wait_time)
            response = requests.post(SILICON_FLOW_API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
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
                
                # 获取实际的 token 使用量
                if 'usage' in data:
                    prompt_tokens = data['usage'].get('prompt_tokens', 0)
                    completion_tokens = data['usage'].get('completion_tokens', 0)
                    total_tokens = data['usage'].get('total_tokens', 0)
                    
                    # 更新 token 监控器
                    token_monitor.add_tokens(total_tokens)
                    
                    # 记录详细的 token 使用情况
                    token_monitor.logger.info(
                        f"Token 使用详情 - 提示词: {prompt_tokens}, "
                        f"生成: {completion_tokens}, "
                        f"总计: {total_tokens}"
                    )
            except Exception as e:
                raise RuntimeError(f"API 返回格式异常: {data}")
            # 返回去除首尾空白的名称字符串
            return result_text.strip()
        else:
            logger.warning(f"第{attempt}次请求失败: HTTP {response.status_code} - {response.text}")
            if attempt == MAX_RETRIES:
                raise RuntimeError(f"API 请求失败，状态码: {response.status_code}")
    # 正常情况下不会执行到此处
