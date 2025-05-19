import os
import re
import json
import argparse
from collections import defaultdict
from core.ai_client import AIClient
from config import USE_OLLAMA, MAX_RETRIES
from tqdm import tqdm
from colorama import init, Fore, Style
from src.main_entry import clear

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
    clear()
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
    input(Fore.YELLOW + "\n请确认以上目录。按回车继续，或按 Ctrl+C 取消。")
    clear()

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
            continue
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        # 检查是否为已删除的图片
        if meta.get('isDeleted', False):
            deleted_images += 1
            continue
            
        # 判断是否属于目标目录
        folder_ids = set(meta.get('folders', []))
        group_ids = folder_ids & all_target_ids
        if not group_ids:
            skipped_images += 1
            continue
        # 只取第一个组（如有多个目录归属，按主目录处理）
        group_id = list(group_ids)[0]
        old_name = meta['name']
        ext = meta['ext']
        main_img = os.path.join(folder, f"{old_name}.{ext}")
        thumb_img = os.path.join(folder, f"{old_name}_thumbnail.{ext}")
        # AI生成新名字，组内重名检测
        retry = 0
        while True:
            suggestion = ai_client.analyze_image(main_img)['description']
            new_name = suggestion.strip().replace(' ', '')
            if new_name not in group_used_names[group_id]:
                break
            retry += 1
            if retry >= MAX_RETRIES:
                new_name = f"{new_name}_{retry+1}"
                break
        # 记录新名字
        group_used_names[group_id].add(new_name)
        # 修改metadata.json
        meta['name'] = new_name
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        # 重命名主图像
        new_main_img = os.path.join(folder, f"{new_name}.{ext}")
        if os.path.exists(main_img):
            os.rename(main_img, new_main_img)
        # 重命名缩略图
        if os.path.exists(thumb_img):
            new_thumb_img = os.path.join(folder, f"{new_name}_thumbnail.{ext}")
            os.rename(thumb_img, new_thumb_img)
        processed_images += 1

    clear()
    # 打印处理结果统计
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
    