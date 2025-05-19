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
# 建议提示词中文数量不超过200个字符
# 同时需要设置下方的MAX_CONTEXT_LENGTH，提示词长度+系统消息+输出，总长度不超过1000个字符
DEFAULT_PROMPT = """你是一个专业的图像命名助手。你的任务是：
1. 严格按照要求生成图像名称
2. 绝对不使用禁止的字样
3. 保持输出的简洁性和诗意性
4. 只返回名称，不要有任何解释或额外文字

为这个作品起名，要求：
1. 文字简洁（不超过六个字）
2. 富有诗意，表达画面意境而非具象描述
3. 避免夸张、华丽词汇，使用干净、素雅、意象化的词语
4. 不带有任何符号
5. 严格禁止使用类似以下字样：
   - "图"
   - "插画"
   - "作品"
   - "画"
6.禁止使用消极与不好的词汇

命名意象参考：
- 主体意象：晶石、云门、镜境、水月
- 次要意象：溪、境、湖、门、镜、石、花
- 色彩氛围：云、霞、晨、暮、春、秋
- 场景类型：梦、境、溪、门、湖

请为图像生成不超过六个字的极简诗意名称。"""

# 图像处理设置
MAX_IMAGE_SIZE = 512  # 图像最长边像素尺寸上限
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}  # 支持处理的图像格式扩展名

# 重试设置
MAX_RETRIES = 3  # 调用 API 出错时的最大重试次数
INITIAL_RETRY_DELAY = 1.0  # 首次重试的延迟时间（秒）
MAX_RETRY_DELAY = 3.0  # 最大重试延迟时间（秒）
IMAGE_PROCESS_DELAY = 0.1  # 处理每张图片之间的延迟时间（秒）

# 上下文长度设置
# 提示：修改上下文长度时请注意：
# 1. 中文字符数 × 2.5 ≈ 所需 token 数
# 2. 建议预留 100-150 tokens 给系统消息和输出
# 3. 总长度建议不超过 1000 tokens
MAX_CONTEXT_LENGTH = 32000  # 模型最大上下文长度
OPTIMAL_CONTEXT_LENGTH = 500  # 建议的上下文长度（基于当前提示词长度）
CONTEXT_WARNING_THRESHOLD = 0.9  # 上下文长度警告阈值（90%）

# ============= API 特定配置 =============

# 选择使用的 API 服务
USE_OLLAMA = True  # 设置为 True 使用本地 Ollama 服务，False 使用硅基流动 API

# 系统消息配置
SYSTEM_MESSAGE = """你是一个专业的图像命名助手。你的任务是：
1. 严格按照要求生成图像名称
2. 绝对不使用禁止的字样
3. 保持输出的简洁性和诗意性
4. 只返回名称，不要有任何解释或额外文字"""

# 模型参数配置
TEMPERATURE = 0.8  # 温度参数，控制输出的随机性（0-1之间，越低越确定）
TOP_P = 0.9  # 核采样参数，控制输出的多样性
REPETITION_PENALTY = 1.1  # 重复惩罚参数，避免重复内容

# 硅基流动 API 配置
SILICON_FLOW_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
SILICON_FLOW_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # 替换为您的 API Key
SILICON_FLOW_MODEL = "qwen2.5-vl-72b"  # 硅基流动 API 模型
SILICON_FLOW_MAX_OUTPUT_TOKENS = 1000  # 硅基流动 API 输出 token 限制

# Token 监控设置（仅在使用硅基流动 API 时生效）
TOKEN_USAGE_LOG = "token_usage.log"  # token 使用量日志文件
TOKEN_LIMIT = 80000  # 每分钟 token 限制
TOKEN_WARNING_THRESHOLD = 0.8  # token 使用量警告阈值（80%）
TOKEN_RESET_INTERVAL = 60  # token 计数重置间隔（秒）
MAX_OUTPUT_TOKENS = 40  # 限制输出 token 数量，4个中文字符约需要 12-16 tokens

# Ollama 配置
OLLAMA_BASE_URL = "http://localhost:11434/api/generate"  # Ollama API 基础 URL
OLLAMA_MODEL = "qwen2.5vl:7b"  # Ollama 模型名称
