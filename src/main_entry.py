import os
import sys
import subprocess

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input("\n按回车键继续...")

def main():
    while True:
        clear()
        print("="*34)
        print("      图像智能批量重命名")
        print("="*34)
        print("\n  [1] 普通批量命名模式")
        print("  [2] Eagle 专用模式")
        print("  [3] 退出")
        print("="*34)
        main_choice = input("请选择主模式 (1-3): ").strip()
        if main_choice == "1":
            mode_type = "normal"
        elif main_choice == "2":
            mode_type = "eagle"
        elif main_choice == "3":
            sys.exit(0)
        else:
            continue

        # 命名方式选择
        while True:
            clear()
            print("="*34)
            print("        选择命名方式")
            print("="*34)
            print("\n  [1] 覆盖模式（Override）\n      用新名称替换原文件名")
            print("\n  [2] 前缀模式（Prefix）\n      新名称作为前缀保留原文件名")
            print("\n  [3] 添加序号（Add Index）\n      添加序号（001-999）")
            print("\n  [4] 返回主菜单")
            print("="*34)
            mode_choice = input("请选择命名方式 (1-4): ").strip()
            if mode_choice == "1":
                rename_mode = "override"
                add_index = False
            elif mode_choice == "2":
                rename_mode = "prefix"
                add_index = False
            elif mode_choice == "3":
                rename_mode = "override"
                add_index = True
            elif mode_choice == "4":
                break
            else:
                continue

            # 进入参数输入
            if mode_type == "normal":
                clear()
                print("="*34)
                print("      普通批量命名模式")
                print("="*34)
                folder = input("请拖入图片文件夹路径，然后回车：\n").strip('"')
                if not os.path.exists(folder):
                    print("错误：文件夹不存在！")
                    pause()
                    continue
                cmd = [sys.executable, "src/main.py", "-i", folder, "-m", rename_mode]
                if add_index:
                    cmd.append("-n")
                subprocess.call(cmd)
                pause()
                break
            else:
                clear()
                print("="*34)
                print("    Eagle 专用批量命名模式")
                print("="*34)
                eagle_root = input("请输入 Eagle 资料库根目录路径（如 E:/AIGC_Project/订阅图库/Eagle资料库）：\n").strip('"')
                if not os.path.exists(eagle_root):
                    print("错误：目录不存在！")
                    pause()
                    continue
                print("请粘贴 Eagle 目录链接（用空格分隔多个链接），然后回车：")
                folder_links = input().strip()
                cmd = [sys.executable, "src/eagle_rename.py", "--root", eagle_root, "--mode", rename_mode]
                if add_index:
                    cmd.append("--add_index")
                # 通过环境变量传递链接
                env = os.environ.copy()
                env["EAGLE_FOLDER_LINKS"] = folder_links
                subprocess.call(cmd, env=env)
                pause()
                break

if __name__ == "__main__":
    main() 