import time
import logging
from datetime import datetime
from config import (
    TOKEN_USAGE_LOG, TOKEN_LIMIT, TOKEN_WARNING_THRESHOLD, TOKEN_RESET_INTERVAL,
    MAX_CONTEXT_LENGTH, OPTIMAL_CONTEXT_LENGTH, CONTEXT_WARNING_THRESHOLD
)

class TokenMonitor:
    def __init__(self):
        self.current_tokens = 0
        self.last_reset_time = time.time()
        self.setup_logging()

    def setup_logging(self):
        """设置日志记录器"""
        self.logger = logging.getLogger('token_monitor')
        self.logger.setLevel(logging.INFO)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(TOKEN_USAGE_LOG)
        file_handler.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def check_and_reset(self):
        """检查是否需要重置计数器"""
        current_time = time.time()
        if current_time - self.last_reset_time >= TOKEN_RESET_INTERVAL:
            if self.current_tokens > 0:  # 只在有使用量时记录
                self.logger.info(f"重置 token 计数。上一分钟使用量: {self.current_tokens}")
            self.current_tokens = 0
            self.last_reset_time = current_time

    def add_tokens(self, tokens):
        """添加使用的 token 数量"""
        self.check_and_reset()
        self.current_tokens += tokens
        
        # 检查是否超过警告阈值
        if self.current_tokens >= TOKEN_LIMIT * TOKEN_WARNING_THRESHOLD:
            self.logger.warning(
                f"Token 使用量接近限制！当前: {self.current_tokens}, "
                f"剩余: {TOKEN_LIMIT - self.current_tokens}, "
                f"使用率: {self.current_tokens/TOKEN_LIMIT*100:.1f}%"
            )
        
        # 记录使用情况（只在有变化时记录）
        if tokens > 0:
            self.logger.info(
                f"Token 使用情况 - 当前: {self.current_tokens}, "
                f"剩余: {TOKEN_LIMIT - self.current_tokens}, "
                f"使用率: {self.current_tokens/TOKEN_LIMIT*100:.1f}%"
            )

    def get_usage_stats(self):
        """获取当前使用统计信息"""
        self.check_and_reset()
        return {
            'current_tokens': self.current_tokens,
            'remaining_tokens': TOKEN_LIMIT - self.current_tokens,
            'usage_percentage': (self.current_tokens / TOKEN_LIMIT) * 100,
            'time_until_reset': TOKEN_RESET_INTERVAL - (time.time() - self.last_reset_time)
        }

# 创建全局 token_monitor 实例
token_monitor = TokenMonitor() 