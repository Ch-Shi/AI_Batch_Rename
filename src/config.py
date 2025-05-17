import os

# API 配置
API_KEY = "sk-xoroghzpskqxxarkzqatjaxlgmdukjjxmrthpnmwrvqizkzq"  # 硅基流动 API 密钥（请替换为实际 API Key）
API_URL = "https://api.siliconflow.cn/v1/chat/completions"  # 硅基流动 ChatCompletions 接口 URL:contentReference[oaicite:9]{index=9}
MODEL = "Pro/Qwen/Qwen2-VL-7B-Instruct"  # 使用的模型名称或ID:contentReference[oaicite:10]{index=10}

# 提示词配置
DEFAULT_PROMPT = "根据图像画面，提取意象，生成不超过四字的中文名称，诗意简洁"

# 图像处理设置
MAX_IMAGE_SIZE = 512  # 图像最长边像素尺寸上限
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}  # 支持处理的图像格式扩展名

# 文件命名配置
RENAME_STRATEGY = "override"  # 重命名策略: "override" 覆盖原名；"prefix" 保留原文件名前缀
ADD_INDEX = True  # 是否在文件名中添加编号

# 重试与日志设置
MAX_RETRIES = 3         # 调用 API 出错时的最大重试次数
LOG_FILE = "rename.log"  # 日志文件路径（当前目录下）
LOG_LEVEL = "INFO"      # 日志级别: DEBUG/INFO/WARNING/ERROR/CRITICAL
