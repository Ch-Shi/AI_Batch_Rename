import os
import sys
import subprocess
import eagle_rename
from colorama import init, Fore, Style

def pause():
    input("\n按回车键继续...")

def main():
    while True:
        print(Fore.CYAN + Style.BRIGHT + "\n==================================")
        print(Fore.CYAN + Style.BRIGHT + "    图像智能批量重命名")
        print(Fore.CYAN + Style.BRIGHT + "==================================")
        print(Fore.CYAN + Style.BRIGHT + "1. 普通批量命名模式")
        print(Fore.CYAN + Style.BRIGHT + "2. Eagle 专用模式")
        print(Fore.CYAN + Style.BRIGHT + "3. 退出")
        choice = input(Fore.YELLOW + Style.BRIGHT + "\n请选择主模式 (1-3): ").strip()
        
        if choice == "1":
            print(Fore.GREEN + Style.BRIGHT + "\n请选择命名方式：")
            print(Fore.GREEN + "1. 覆盖模式 - 直接使用 AI 生成的新名称")
            print(Fore.GREEN + "2. 前缀模式 - 在原有文件名前添加 AI 生成的前缀")
            print(Fore.GREEN + "3. 添加序号 - 在 AI 生成的新名称后添加序号")
            mode = input(Fore.YELLOW + Style.BRIGHT + "请选择命名方式 (1-3): ").strip()
            
            if mode not in ["1", "2", "3"]:
                print(Fore.RED + Style.BRIGHT + "无效的命名方式选择！")
                input(Fore.YELLOW + "\n按回车返回...")
                continue
                
            folder_path = input(Fore.YELLOW + Style.BRIGHT + "\n请输入要处理的文件夹路径：").strip()
            if not os.path.exists(folder_path):
                print(Fore.RED + Style.BRIGHT + "文件夹路径不存在！")
                input(Fore.YELLOW + "\n按回车返回...")
                continue
                
            add_index = mode == "3"
            main.main(folder_path, mode, add_index)
            input(Fore.YELLOW + "\n按回车返回主菜单...")
            
        elif choice == "2":
            print(Fore.YELLOW + Style.BRIGHT + "\n请输入 " + Fore.CYAN + Style.BRIGHT + "Eagle 资料库根目录路径" + Fore.YELLOW + Style.BRIGHT + "，或直接从 " + Fore.CYAN + Style.BRIGHT + "Eagle 软件窗口" + Fore.YELLOW + Style.BRIGHT + "中拖入任意文件/图片后回车：")
            eagle_root = input().strip()
            
            print(Fore.YELLOW + Style.BRIGHT + "\n请从 " + Fore.CYAN + Style.BRIGHT + "Eagle 软件中复制目录链接" + Fore.YELLOW + Style.BRIGHT + "（可多选，用空格分隔），然后回车：")
            print(Fore.GREEN + Style.BRIGHT + "提示：" + Fore.YELLOW + "在 Eagle 中右键点击目录，选择" + Fore.CYAN + Style.BRIGHT + "「复制链接」" + Fore.YELLOW + "即可获取目录链接")
            folder_links = input().strip()
            
            # 设置环境变量
            os.environ["EAGLE_FOLDER_LINKS"] = folder_links
            
            # 调用 Eagle 重命名模块
            eagle_rename.main(eagle_root)
            input(Fore.YELLOW + "\n按回车返回主菜单...")
            
        elif choice == "3":
            print(Fore.GREEN + Style.BRIGHT + "\n感谢使用，再见！")
            break
            
        else:
            print(Fore.RED + Style.BRIGHT + "无效的选择，请重新输入！")
            input(Fore.YELLOW + "\n按回车返回...")

if __name__ == "__main__":
    main() 