import os

# ============= 通用配置 =============

# 文件处理配置
SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
DEFAULT_MODE = 'override'  # 默认命名策略：override 或 prefix
ADD_INDEX = False  # 是否添加序号

# 日志配置
LOG_FILE = 'rename.log'  # 日志文件路径
LOG_LEVEL = 'INFO'  # 日志级别: DEBUG/INFO/WARNING/ERROR/CRITICAL

# 提示词配置
DEFAULT_PROMPT = """Generate a poetic Chinese name for this image.

Requirements:
1. Return ONLY the name, no explanations or descriptions
2. The name should be poetic and express the mood/atmosphere
3. Use clean, elegant words
4. No punctuation marks
5. Maximum 6 Chinese characters

Naming elements:
- Main elements: crystal, cloud gate, mirror realm, water moon
- Secondary elements: stream, realm, lake, gate, mirror, stone, flower
- Color/mood: cloud, sunset, dawn, dusk, spring, autumn
- Scene types: dream, realm, stream, gate, lake

Example names:
- Crystal Stream (晶溪)
- Cloud Gate (云门)
- Water Moon Mirror (水月镜)

Return ONLY the Chinese name, nothing else."""

# 图像处理设置
MAX_IMAGE_SIZE = 512  # 图像最长边像素尺寸上限
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}  # 支持处理的图像格式扩展名

# 重试设置
MAX_RETRIES = 3  # 调用 API 出错时的最大重试次数
INITIAL_RETRY_DELAY = 1.0  # 首次重试的延迟时间（秒）
MAX_RETRY_DELAY = 3.0  # 最大重试延迟时间（秒）
IMAGE_PROCESS_DELAY = 0.1  # 处理每张图片之间的延迟时间（秒）

# Token 监控设置
TOKEN_USAGE_LOG = "token_usage.log"  # token 使用量日志文件
TOKEN_LIMIT = 80000  # 每分钟 token 限制
TOKEN_WARNING_THRESHOLD = 0.8  # token 使用量警告阈值（80%）
TOKEN_RESET_INTERVAL = 60  # token 计数重置间隔（秒）
MAX_OUTPUT_TOKENS = 40  # 限制输出 token 数量，4个中文字符约需要 12-16 tokens

# 上下文长度设置
MAX_CONTEXT_LENGTH = 32000  # 模型最大上下文长度
OPTIMAL_CONTEXT_LENGTH = 100  # 建议的上下文长度
CONTEXT_WARNING_THRESHOLD = 0.9  # 上下文长度警告阈值（90%）

# ============= API 特定配置 =============

# 选择使用的 API 服务
USE_OLLAMA = True  # 设置为 True 使用本地 Ollama 服务，False 使用硅基流动 API

# 硅基流动 API 配置
SILICON_FLOW_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
SILICON_FLOW_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # 替换为您的 API Key
SILICON_FLOW_MODEL = "qwen2.5-vl-72b"  # 硅基流动 API 模型
SILICON_FLOW_MAX_OUTPUT_TOKENS = 1000  # 硅基流动 API 输出 token 限制

# Ollama 配置
OLLAMA_BASE_URL = "http://localhost:11434/api/generate"  # Ollama API 基础 URL
OLLAMA_MODEL = "qwen2.5vl:3b"  # Ollama 模型名称
