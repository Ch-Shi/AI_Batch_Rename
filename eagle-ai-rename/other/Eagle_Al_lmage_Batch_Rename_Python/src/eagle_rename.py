import os
import re
import json
import argparse
from collections import defaultdict
from core.ai_client import AIClient
from config import USE_OLLAMA, MAX_RETRIES, SUPPORTED_FORMATS
from tqdm import tqdm
from colorama import init, Fore, Style
from utils.enhanced_logger import enhanced_logger, LogType  # 正确导入LogType

init(autoreset=True)

def parse_folder_links(links):
    """解析用户输入，提取所有 eagle://folder/xxxxxx 目录ID，支持空格分隔"""
    ids = []
    # 按空格分割每个链接
    for token in links.strip().split():
        m = re.search(r'eagle://folder/([A-Z0-9]+)', token)
        if m:
            ids.append(m.group(1))
        else:
            # 兼容 http://localhost:41595/folder?id=XXXX 这种格式
            m2 = re.search(r'folder\?id=([A-Z0-9]+)', token)
            if m2:
                ids.append(m2.group(1))
    return ids

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=str, help='Eagle library root folder')
    parser.add_argument('--mode', type=str, default='override', help='rename mode')
    parser.add_argument('--add_index', action='store_true', help='add index')
    return parser.parse_args()

def get_all_subfolder_ids(root_ids, eagle_metadata):
    """递归获取所有子目录ID（含自身）"""
    result = set(root_ids)  # 首先添加所有根目录ID
    
    def get_all_children(folder):
        """递归获取文件夹的所有子目录ID"""
        children_ids = set()
        if folder.get('children'):
            for child in folder['children']:
                children_ids.add(child['id'])
                children_ids.update(get_all_children(child))
        return children_ids
    
    def dfs(folders):
        for folder in folders:
            if folder['id'] in root_ids:
                # 获取当前目录的所有子目录ID
                children_ids = get_all_children(folder)
                result.update(children_ids)
            if folder.get('children'):
                dfs(folder['children'])
    
    dfs(eagle_metadata['folders'])
    return result

def find_image_folders(images_root):
    """返回所有 .info 结尾的图片文件夹绝对路径"""
    return [os.path.join(images_root, d) for d in os.listdir(images_root)
            if d.endswith('.info') and os.path.isdir(os.path.join(images_root, d))]

def build_id2name_map(eagle_metadata):
    """递归构建 目录ID->名称 的映射"""
    id2name = {}
    def dfs(folders):
        for folder in folders:
            id2name[folder['id']] = folder['name']
            if folder.get('children'):
                dfs(folder['children'])
    dfs(eagle_metadata['folders'])
    return id2name

def process_eagle_rename(library_path, target_folder_ids):
    # 1. 读取 Eagle 根 metadata.json
    with open(os.path.join(library_path, 'metadata.json'), 'r', encoding='utf-8') as f:
        eagle_metadata = json.load(f)
    all_target_ids = get_all_subfolder_ids(target_folder_ids, eagle_metadata)
    id2name = build_id2name_map(eagle_metadata)
    print(Fore.CYAN + Style.BRIGHT + "\n目标目录：")
    for tid in target_folder_ids:
        print(Fore.CYAN + f"- {tid}：{id2name.get(tid, '[未知目录]')}")
    print(Fore.CYAN + "包含子目录：")
    for tid in all_target_ids:
        print(Fore.CYAN + f"- {tid}：{id2name.get(tid, '[未知目录]')}")
    
    # 记录目标目录信息到日志
    enhanced_logger.log(
        LogType.INFO,
        f"开始处理Eagle资料库: {os.path.basename(library_path)}",
        context="session_info",
        file_path=library_path
    )
    for tid in target_folder_ids:
        enhanced_logger.log(
            LogType.INFO,
            f"目标目录: {id2name.get(tid, '[未知目录]')} ({tid})",
            context="target_folder",
            is_console=False  # 不在控制台显示，只记录到日志
        )
    
    input(Fore.YELLOW + "\n请确认以上目录。按回车继续，或按 Ctrl+C 取消。")

    # 2. 遍历所有图片文件夹
    images_root = os.path.join(library_path, 'images')
    image_folders = find_image_folders(images_root)
    group_used_names = defaultdict(set)
    ai_client = AIClient(use_ollama=USE_OLLAMA)
    
    # 统计信息
    total_images = len(image_folders)
    processed_images = 0
    skipped_images = 0
    deleted_images = 0

    for folder in tqdm(image_folders, desc="Eagle AI重命名"):
        meta_path = os.path.join(folder, 'metadata.json')
        if not os.path.exists(meta_path):
            skipped_images += 1
            enhanced_logger.log_warning(
                f"缺少元数据文件: {folder}", 
                context="metadata_missing",
                file_path=folder
            )
            continue
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        except Exception as e:
            enhanced_logger.log_error(
                f"读取元数据失败: {folder}", 
                error=e,
                context="metadata_read_error",
                file_path=meta_path
            )
            skipped_images += 1
            continue
        
        # 检查是否为已删除的图片
        if meta.get('isDeleted', False):
            deleted_images += 1
            enhanced_logger.log_warning(
                f"跳过已删除图片: {folder}",
                context="deleted_image",
                file_path=folder,
                is_console=False  # 不在控制台显示，只记录到日志
            )
            continue
        
        # 判断是否属于目标目录
        folder_ids = set(meta.get('folders', []))
        group_ids = folder_ids & all_target_ids
        if not group_ids:
            skipped_images += 1
            enhanced_logger.log_warning(
                f"跳过非目标目录图片: {folder}",
                context="not_target_folder",
                file_path=folder,
                is_console=False  # 不在控制台显示，只记录到日志
            )
            continue
        
        # 只取第一个组（如有多个目录归属，按主目录处理）
        group_id = list(group_ids)[0]
        # 记录所属组信息
        group_name = id2name.get(group_id, '[未知目录]')
        
        old_name = meta['name']
        ext = meta['ext']
        main_img = os.path.join(folder, f"{old_name}.{ext}")
        
        # 缩略图只有.png格式
        thumb_img = os.path.join(folder, f"{old_name}_thumbnail.png")
        has_thumb = os.path.exists(thumb_img)
        
        # 跳过非图片格式
        if not any(main_img.lower().endswith(e) for e in SUPPORTED_FORMATS):
            skipped_images += 1
            enhanced_logger.log_warning(
                f"跳过不支持的图片格式: {main_img}",
                context="unsupported_format",
                file_path=main_img,
                group_id=group_id
            )
            continue
        
        # 检查主图是否存在
        if not os.path.exists(main_img):
            enhanced_logger.log_error(
                f"主图文件不存在: {main_img}",
                context="main_image_missing",
                file_path=main_img,
                group_id=group_id
            )
            skipped_images += 1
            continue
        
        # 记录处理开始
        enhanced_logger.log(
            LogType.INFO,
            f"开始处理图片: {os.path.basename(main_img)}",
            context="process_start",
            file_path=main_img,
            group_id=group_id,
            old_name=old_name,
            is_console=False  # 不在控制台显示，只记录到日志
        )
            
        # AI生成新名字，组内重名检测
        retry = 0
        while True:
            try:
                result = ai_client.analyze_image(main_img)
                suggestion = result['description']
                enhanced_logger.log_image_analysis(
                    folder, main_img, result=result, group_id=group_id
                )
            except Exception as e:
                enhanced_logger.log_image_analysis(
                    folder, main_img, error=e, group_id=group_id
                )
                skipped_images += 1
                suggestion = None
                break
            
            if suggestion is None:
                break
            
            new_name = suggestion.strip().replace(' ', '')
            
            # 记录生成的建议名称
            enhanced_logger.log(
                LogType.INFO,
                f"AI生成名称: {new_name} (原名: {old_name})",
                context="name_suggestion",
                file_path=main_img,
                old_name=old_name,
                new_name=new_name,
                group_id=group_id
            )
            
            if new_name not in group_used_names[group_id]:
                break
            
            # 记录重名情况
            retry += 1
            enhanced_logger.log_warning(
                f"名称 '{new_name}' 在组 '{group_name}' 中已存在，尝试重新生成 ({retry}/{MAX_RETRIES})",
                context="name_collision",
                file_path=main_img,
                old_name=old_name,
                new_name=new_name,
                group_id=group_id
            )
            
            if retry >= MAX_RETRIES:
                # 最后一次尝试，添加序号
                new_name = f"{new_name}_{retry+1}"
                enhanced_logger.log_warning(
                    f"达到最大重试次数，使用添加序号的方式: {new_name}",
                    context="max_retries_reached",
                    file_path=main_img,
                    old_name=old_name,
                    new_name=new_name,
                    group_id=group_id
                )
                break
        
        if suggestion is None:
            continue
        
        # 记录新名字
        group_used_names[group_id].add(new_name)

        # 状态追踪
        meta_updated = False
        main_renamed = False
        thumb_renamed = False

        # 1. 修改metadata.json
        try:
            meta['name'] = new_name
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
            meta_updated = True
            enhanced_logger.log_metadata_update(
                meta_path, old_name, new_name, 
                success=True, group_id=group_id
            )
        except Exception as e:
            enhanced_logger.log_metadata_update(
                meta_path, old_name, new_name, 
                success=False, error=e, group_id=group_id
            )
            skipped_images += 1
            continue

        # 2. 重命名主图像
        new_main_img = os.path.join(folder, f"{new_name}.{ext}")
        try:
            os.rename(main_img, new_main_img)
            main_renamed = True
            enhanced_logger.log_rename(
                "主图", main_img, new_main_img, 
                success=True, group_id=group_id
            )
        except Exception as e:
            enhanced_logger.log_rename(
                "主图", main_img, new_main_img, 
                success=False, error=e, group_id=group_id
            )
            
            # 恢复metadata.json
            try:
                meta['name'] = old_name
                with open(meta_path, 'w', encoding='utf-8') as f:
                    json.dump(meta, f, ensure_ascii=False, indent=2)
                enhanced_logger.log_recovery_operation(
                    "元数据", meta_path, old_name, new_name,
                    success=True, group_id=group_id
                )
            except Exception as restore_err:
                enhanced_logger.log_recovery_operation(
                    "元数据", meta_path, old_name, new_name,
                    success=False, error=restore_err, group_id=group_id
                )
            
            skipped_images += 1
            continue

        # 3. 重命名缩略图（如果存在）
        if has_thumb:
            new_thumb_img = os.path.join(folder, f"{new_name}_thumbnail.png")
            try:
                os.rename(thumb_img, new_thumb_img)
                thumb_renamed = True
                enhanced_logger.log_rename(
                    "缩略图", thumb_img, new_thumb_img, 
                    success=True, group_id=group_id
                )
            except Exception as e:
                enhanced_logger.log_rename(
                    "缩略图", thumb_img, new_thumb_img, 
                    success=False, error=e, group_id=group_id
                )
                
                # 恢复已进行的更改：主图和元数据
                recovery_errors = []
                
                # 恢复主图
                try:
                    os.rename(new_main_img, main_img)
                    enhanced_logger.log_recovery_operation(
                        "主图", main_img, old_name, new_name,
                        success=True, group_id=group_id
                    )
                except Exception as restore_err:
                    recovery_errors.append(f"主图恢复失败: {restore_err}")
                    enhanced_logger.log_recovery_operation(
                        "主图", main_img, old_name, new_name,
                        success=False, error=restore_err, group_id=group_id
                    )
                
                # 恢复元数据
                try:
                    meta['name'] = old_name
                    with open(meta_path, 'w', encoding='utf-8') as f:
                        json.dump(meta, f, ensure_ascii=False, indent=2)
                    enhanced_logger.log_recovery_operation(
                        "元数据", meta_path, old_name, new_name,
                        success=True, group_id=group_id
                    )
                except Exception as restore_err:
                    recovery_errors.append(f"元数据恢复失败: {restore_err}")
                    enhanced_logger.log_recovery_operation(
                        "元数据", meta_path, old_name, new_name,
                        success=False, error=restore_err, group_id=group_id
                    )
                
                skipped_images += 1
                continue

        # 记录整体处理结果
        enhanced_logger.log_success(
            f"完成处理: {old_name} -> {new_name}",
            context="image_processed",
            file_path=folder,
            old_name=old_name,
            new_name=new_name,
            group_id=group_id
        )
        processed_images += 1

    # 记录会话结束与统计信息
    stats = enhanced_logger.finish_session(
        total_images, processed_images, skipped_images, deleted_images
    )
    
    # 打印处理结果统计（使用原始方式，增强日志模块已经打印了详细统计）
    print(Fore.GREEN + f"\n处理完成！")
    print(Fore.GREEN + f"总图片数：{total_images}")
    print(Fore.GREEN + f"已处理：{processed_images}")
    print(Fore.YELLOW + f"已跳过：{skipped_images}（不在目标目录中）")
    print(Fore.YELLOW + f"已删除：{deleted_images}（标记为删除的图片）")
    input(Fore.YELLOW + "\n按回车键返回主菜单...")
    print(Fore.GREEN + "\n✓ 批量重命名完成！")

def print_folder_tree(root_ids, eagle_metadata):
    """打印目录树结构，供用户确认"""
    def dfs(folders, level=0, parent_selected=False):
        for folder in folders:
            selected = folder['id'] in root_ids or parent_selected
            if selected:
                print('  ' * level + '- ' + folder['name'])
            if folder.get('children'):
                dfs(folder['children'], level+1, selected)
    print("\n将处理以下目录（及其子目录）：")
    dfs(eagle_metadata['folders'])
    print("\n请确认以上目录。按回车继续，或按 Ctrl+C 取消。")
    input()

def find_eagle_library_root(path):
    """从任意路径向上查找，直到找到以 .library 结尾的文件夹"""
    # 移除路径中的引号
    path = path.strip('"').strip("'")
    # 转换为绝对路径
    path = os.path.abspath(path)
    
    # 如果是文件，先获取其所在目录
    if os.path.isfile(path):
        path = os.path.dirname(path)
    
    # 如果是.info目录，继续向上查找
    if path.endswith('.info'):
        path = os.path.dirname(path)
    
    # 如果是images目录，继续向上查找
    if os.path.basename(path) == 'images':
        path = os.path.dirname(path)
    
    # 向上查找.library目录
    while True:
        if os.path.isdir(path) and path.lower().endswith('.library'):
            return path
        parent = os.path.dirname(path)
        if parent == path:  # 已经到达根目录
            return None
        path = parent

def main(eagle_root=None):
    args = get_args()
    if eagle_root is None:
        eagle_root = args.root
    if not eagle_root:
        while True:
            input_path = input().strip()
            eagle_root = find_eagle_library_root(input_path)
            if eagle_root and os.path.exists(os.path.join(eagle_root, 'metadata.json')):
                print(f"\n✓ 已找到 Eagle 资料库：{os.path.basename(eagle_root)}")
                break
            print("✗ 未能识别为有效的 Eagle 资料库目录，请重新输入或拖入 Eagle 文件：")
    # 确保 eagle_root 是目录而不是文件
    if os.path.isfile(eagle_root):
        eagle_root = os.path.dirname(eagle_root)
    # 确保 eagle_root 是 .library 目录
    if not eagle_root.lower().endswith('.library'):
        eagle_root = find_eagle_library_root(eagle_root)
        if not eagle_root:
            print("✗ 错误：无法找到有效的 Eagle 资料库目录")
            exit(1)
    # 目录链接优先从环境变量获取
    folder_links = os.environ.get("EAGLE_FOLDER_LINKS")
    if not folder_links:
        folder_links = input().strip()
    target_folder_ids = parse_folder_links(folder_links)
    # 打印目录树供用户确认
    print("\n将处理以下目录（及其子目录）：")
    with open(os.path.join(eagle_root, 'metadata.json'), 'r', encoding='utf-8') as f:
        eagle_metadata = json.load(f)
    print_folder_tree(target_folder_ids, eagle_metadata)
    process_eagle_rename(eagle_root, target_folder_ids)
    print("\n✓ 批量重命名完成！")

if __name__ == "__main__":
    main() 
    