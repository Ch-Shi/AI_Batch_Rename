import os
import re

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
    # 检测命名冲突：若目标文件名已存在，则添加递增数字后缀避免冲突
    new_base = base_name
    counter = 1
    while os.path.exists(os.path.join(dir_name, new_base + ext)):
        new_base = f"{base_name}_{counter}"
        counter += 1
    # 最终的新文件名（含扩展名）
    new_name = new_base + ext
    return os.path.join(dir_name, new_name)
