import os
import sys
import argparse
import time
from datetime import datetime
from tqdm import tqdm
from config import (
    DEFAULT_MODE, ADD_INDEX, ALLOWED_EXTENSIONS,
    IMAGE_PROCESS_DELAY, TOKEN_WARNING_THRESHOLD,
    USE_OLLAMA, MAX_RETRIES
)
from core.image_utils import compress_image_to_base64
from core.ai_client import AIClient
from core.naming import generate_new_name, NameManager
from utils.logger import logger
from token_monitor import token_monitor

def get_image_files(directory):
    """获取目录下所有支持的图片文件"""
    image_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
                image_files.append(os.path.join(root, file))
    return sorted(image_files)

def process_image(image_path, ai_client, mode, add_index, index=None):
    """处理单个图片"""
    try:
        # 这里添加您的图片处理逻辑
        # 假设每次处理使用约 1000 tokens
        estimated_tokens = 1000
        token_monitor.add_tokens(estimated_tokens)
        
        # 获取当前使用统计
        stats = token_monitor.get_usage_stats()
        if stats['usage_percentage'] >= TOKEN_WARNING_THRESHOLD * 100:
            print(f"警告：Token 使用量已达到 {stats['usage_percentage']:.1f}%")
            time.sleep(IMAGE_PROCESS_DELAY * 2)  # 增加延迟时间
        
        # 分析图像并获取描述
        result = ai_client.analyze_image(image_path)
        suggestion = result["description"]
        
        # 处理重名情况
        retry_count = 0
        new_path = None
        while new_path is None and retry_count < MAX_RETRIES:
            # 根据策略生成新的文件名
            new_path = generate_new_name(
                image_path, suggestion,
                strategy=mode, add_index=add_index,
                index=index
            )
            if new_path is None:
                # 需要重新生成名称
                retry_count += 1
                if retry_count < MAX_RETRIES:
                    print(f"检测到重名，正在重新生成名称... (尝试 {retry_count}/{MAX_RETRIES})")
                    result = ai_client.analyze_image(image_path)
                    suggestion = result["description"]
                else:
                    # 最后一次尝试，使用带序号的名字
                    new_path = generate_new_name(
                        image_path, suggestion,
                        strategy=mode, add_index=add_index,
                        index=index
                    )
        
        # 重命名文件
        os.rename(image_path, new_path)
        logger.info(f"重命名成功: {os.path.basename(image_path)} -> {os.path.basename(new_path)}")
        return True, suggestion
    except Exception as e:
        error_msg = f"重命名失败: {os.path.basename(image_path)} - 错误: {str(e)}"
        logger.error(error_msg)
        # 记录失败信息到专门的失败日志文件
        with open('rename_failures.log', 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {error_msg}\n")
        return False, str(e)

def main():
    parser = argparse.ArgumentParser(description='批量图像智能重命名工具')
    parser.add_argument('-i', '--input_dir', required=True, help='输入目录路径')
    parser.add_argument('-m', '--mode', default=DEFAULT_MODE, choices=['override', 'prefix'],
                      help='命名策略：override（覆盖）或 prefix（前缀）')
    parser.add_argument('-n', '--add_index', action='store_true', help='是否添加序号')
    args = parser.parse_args()

    # 检查输入目录
    if not os.path.exists(args.input_dir):
        print(f"错误：目录 '{args.input_dir}' 不存在！")
        return

    # 获取所有图片文件
    image_files = get_image_files(args.input_dir)
    if not image_files:
        print(f"错误：在目录 '{args.input_dir}' 中未找到支持的图片文件！")
        return

    print(f"\n找到 {len(image_files)} 个图片文件")
    print(f"使用模式: {args.mode}")
    if args.add_index:
        print("已启用序号添加")

    # 初始化 AI 客户端
    ai_client = AIClient(use_ollama=USE_OLLAMA)

    # 处理图片
    success_count = 0
    fail_count = 0
    index = 1 if args.add_index else None

    print("\n开始处理图片...")
    with tqdm(total=len(image_files), desc="处理进度") as pbar:
        for image_path in image_files:
            success, result = process_image(
                image_path, ai_client, args.mode, args.add_index, index
            )
            
            if success:
                success_count += 1
                if args.add_index:
                    index += 1
            else:
                fail_count += 1
            
            pbar.update(1)
            pbar.set_postfix({
                "成功": success_count,
                "失败": fail_count,
                "当前": os.path.basename(image_path)
            })
            
            time.sleep(IMAGE_PROCESS_DELAY)
    
    # 打印重名统计信息
    name_manager = NameManager()
    name_manager.print_summary()
    
    print(f"\n处理完成！成功: {success_count}, 失败: {fail_count}")

if __name__ == "__main__":
    main()