import logging
from config import LOG_FILE, LOG_LEVEL

# 设置全局日志记录器
logger = logging.getLogger("ImageRenamer")
level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
logger.setLevel(level)

# 文件日志处理器
file_handler = logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8')
file_handler.setLevel(level)
# 控制台日志处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(level)

# 定义日志输出格式（时间，日志级别，消息）
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 将处理器添加到记录器
logger.addHandler(file_handler)
logger.addHandler(console_handler)
