import os
import re
import logging
from datetime import datetime
from config import MAX_RETRIES
from utils.logger import logger

# 设置重名日志记录器
duplicate_logger = logging.getLogger('duplicate_names')
duplicate_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('duplicate_names.log', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
duplicate_logger.addHandler(file_handler)

class NameManager:
    def __init__(self):
        self.used_names = set()
        self.duplicate_count = 0
        self.duplicate_files = []

    def add_name(self, name):
        """添加已使用的名称"""
        self.used_names.add(name)

    def is_duplicate(self, name):
        """检查名称是否重复"""
        return name in self.used_names

    def record_duplicate(self, original_path, final_name):
        """记录重名情况"""
        self.duplicate_count += 1
        self.duplicate_files.append({
            'original': os.path.basename(original_path),
            'final': final_name
        })
        duplicate_logger.info(
            f"重名处理: {os.path.basename(original_path)} -> {final_name}"
        )

    def print_summary(self):
        """打印重名统计信息"""
        if self.duplicate_count > 0:
            print("\n重名处理统计:")
            print(f"总重名文件数: {self.duplicate_count}")
            print("\n重名文件列表:")
            for file in self.duplicate_files:
                print(f"原文件名: {file['original']}")
                print(f"最终名称: {file['final']}")
                print("-" * 30)

# 创建全局名称管理器实例
name_manager = NameManager()

def clean_filename(filename):
    """
    清理文件名，移除Windows不允许的特殊字符
    """
    # 移除Windows不允许的字符: \ / : * ? " < > |
    filename = re.sub(r'[\\/:*?"<>|]', '', filename)
    # 移除其他可能导致问题的字符
    filename = re.sub(r'[\r\n\t]', '', filename)
    # 移除首尾空格和点
    filename = filename.strip('. ')
    return filename

def generate_new_name(original_path, suggestion, strategy="override", add_index=False, index=None):
    """
    根据指定的命名策略和AI给出的名称建议，生成新的文件完整路径。
    original_path: 原文件的路径。
    suggestion: 模型生成的名称（不含扩展名）。
    strategy: 重命名策略 ("override"或"prefix")。
    add_index: 是否在文件名中添加编号。
    index: 当前文件的序号（从1开始），用于生成编号后缀（当 add_index=True 时有效）。
    返回新的文件路径字符串。
    """
    dir_name = os.path.dirname(original_path)
    orig_base = os.path.splitext(os.path.basename(original_path))[0]
    ext = os.path.splitext(original_path)[1]  # 保留原始扩展名（含点）
    # 清理模型建议的名称字符串（去除引号及多余空格）
    name = clean_filename(suggestion.strip().strip('\"""'))
    # 按策略生成新文件名（无扩展名部分）
    if strategy == "override":
        # 覆盖原名：直接使用建议名；如建议名为空则用原名
        base_name = name or orig_base
    elif strategy == "prefix":
        # 前缀模式：原文件名 + "_" + 建议名；如建议名为空仍使用原名
        base_name = f"{orig_base}_{name}" if name else orig_base
    else:
        # 未知策略，退化为覆盖策略
        base_name = name or orig_base
    # 如果需要添加编号且提供了序号
    if add_index and index is not None:
        # 在末尾添加零填充的序号（默认3位，可以根据需要调整位数）
        base_name = f"{base_name}{str(index).zfill(3)}"
    # 处理重名情况
    new_base = base_name
    counter = 1
    retry_count = 0
    
    while os.path.exists(os.path.join(dir_name, new_base + ext)) or name_manager.is_duplicate(new_base):
        if retry_count < MAX_RETRIES:
            # 记录重名情况
            name_manager.record_duplicate(original_path, new_base)
            # 返回 None 表示需要重新生成名称
            return None
        else:
            # 超过重试次数，添加序号
            new_base = f"{base_name}_{counter}"
            counter += 1
    
    # 添加新名称到已使用集合
    name_manager.add_name(new_base)
    
    # 最终的新文件名（含扩展名）
    new_name = new_base + ext
    return os.path.join(dir_name, new_name)
