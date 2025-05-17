import os
import argparse
from config import config
from core.image_utils import compress_image_to_base64
from core.ai_client import get_image_caption
from core.naming import generate_new_name
from utils.logger import logger

def main():
    parser = argparse.ArgumentParser(description="批量图像智能重命名脚本")
    parser.add_argument("-i", "--input_dir", required=True, help="要处理的图像文件夹路径")
    parser.add_argument("-m", "--mode", choices=["override", "prefix"], help="命名策略：override(覆盖原名)或prefix(保留前缀)")
    parser.add_argument("-n", "--add_index", action="store_true", help="是否在文件名中添加编号")
    args = parser.parse_args()

    input_dir = args.input_dir
    # 确定命名策略和是否添加编号（命令行参数优先，否则采用配置默认值）
    mode = args.mode if args.mode else config.RENAME_STRATEGY
    add_index_flag = True if args.add_index else config.ADD_INDEX

    logger.info(f"开始处理目录: {input_dir}, 策略: {mode}, 添加编号: {add_index_flag}")
    if not os.path.isdir(input_dir):
        logger.error(f"输入路径不存在或不是文件夹: {input_dir}")
        return

    # 遍历输入目录及子目录，收集所有符合条件的图像文件路径
    image_files = []
    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext in config.ALLOWED_EXTENSIONS:
                image_files.append(os.path.join(root, filename))
    if not image_files:
        logger.error("未找到支持的图像文件，请检查输入目录。")
        return

    total = len(image_files)
    success_count = 0
    failure_count = 0
    # 批量处理每个图像文件
    for idx, file_path in enumerate(image_files, start=1):
        try:
            # 压缩图像并获取 base64 数据URI
            data_uri = compress_image_to_base64(file_path)
            # 调用模型获取图像的名称建议
            suggestion = get_image_caption(data_uri)
            # 根据策略生成新的文件名（完整路径）
            new_path = generate_new_name(
                file_path, suggestion,
                strategy=mode, add_index=add_index_flag,
                index=(idx if add_index_flag else None)
            )
            # 重命名文件
            os.rename(file_path, new_path)
            success_count += 1
            logger.info(f"[{idx}/{total}] 重命名成功: {os.path.basename(file_path)} -> {os.path.basename(new_path)}")
        except Exception as e:
            failure_count += 1
            logger.error(f"[{idx}/{total}] 重命名失败: {os.path.basename(file_path)} - 错误: {e}")
    logger.info(f"处理完成。成功: {success_count} 张, 失败: {failure_count} 张。")

if __name__ == "__main__":
    main()
