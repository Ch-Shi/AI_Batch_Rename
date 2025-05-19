import os
import re
import json
from collections import defaultdict
from core.ai_client import AIClient
from config import USE_OLLAMA, MAX_RETRIES
from tqdm import tqdm

def parse_folder_links(links):
    """解析用户输入，提取所有 eagle://folder/xxxxxx 目录ID"""
    ids = []
    for line in links.splitlines():
        m = re.search(r'eagle://folder/([A-Z0-9]+)', line)
        if m:
            ids.append(m.group(1))
    return ids

def get_all_subfolder_ids(root_ids, eagle_metadata):
    """递归获取所有子目录ID（含自身）"""
    result = set()
    def dfs(folders):
        for folder in folders:
            if folder['id'] in root_ids:
                result.add(folder['id'])
                if folder.get('children'):
                    dfs(folder['children'])
            else:
                if folder.get('children'):
                    dfs(folder['children'])
    dfs(eagle_metadata['folders'])
    return result

def find_image_folders(images_root):
    """返回所有 .info 结尾的图片文件夹绝对路径"""
    return [os.path.join(images_root, d) for d in os.listdir(images_root)
            if d.endswith('.info') and os.path.isdir(os.path.join(images_root, d))]

def process_eagle_rename(library_path, target_folder_ids):
    # 1. 读取 Eagle 根 metadata.json
    with open(os.path.join(library_path, 'metadata.json'), 'r', encoding='utf-8') as f:
        eagle_metadata = json.load(f)
    all_target_ids = get_all_subfolder_ids(target_folder_ids, eagle_metadata)

    # 2. 遍历所有图片文件夹
    images_root = os.path.join(library_path, 'images')
    image_folders = find_image_folders(images_root)
    group_used_names = defaultdict(set)
    ai_client = AIClient(use_ollama=USE_OLLAMA)

    for folder in tqdm(image_folders, desc="Eagle AI重命名"):
        meta_path = os.path.join(folder, 'metadata.json')
        if not os.path.exists(meta_path):
            continue
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        # 判断是否属于目标目录
        folder_ids = set(meta.get('folders', []))
        group_ids = folder_ids & all_target_ids
        if not group_ids:
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
        # 可选：日志输出

if __name__ == "__main__":
    print("请在Eagle中复制目录链接（可多行），粘贴后回车结束：")
    lines = []
    while True:
        try:
            line = input()
            if not line.strip():
                break
            lines.append(line)
        except EOFError:
            break
    folder_links = '\n'.join(lines)
    target_folder_ids = parse_folder_links(folder_links)
    library_path = input("请输入Eagle资料库根目录路径：").strip()
    process_eagle_rename(library_path, target_folder_ids)
    print("重命名完成！") 