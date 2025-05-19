import os
import sys
import subprocess
import eagle_rename

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input("\n按回车键继续...")

def main():
    while True:
        print("\n==================================")
        print("    图像智能批量重命名")
        print("==================================")
        print("1. 普通批量命名模式")
        print("2. Eagle 专用模式")
        print("3. 退出")
        choice = input("\n请选择主模式 (1-3): ").strip()
        
        if choice == "1":
            print("\n请选择命名方式：")
            print("1. 覆盖模式 - 直接使用 AI 生成的新名称")
            print("2. 前缀模式 - 在原有文件名前添加 AI 生成的前缀")
            print("3. 添加序号 - 在 AI 生成的新名称后添加序号")
            mode = input("请选择命名方式 (1-3): ").strip()
            
            if mode not in ["1", "2", "3"]:
                print("无效的命名方式选择！")
                continue
                
            folder_path = input("\n请输入要处理的文件夹路径：").strip()
            if not os.path.exists(folder_path):
                print("文件夹路径不存在！")
                continue
                
            add_index = mode == "3"
            main.main(folder_path, mode, add_index)
            
        elif choice == "2":
            print("\n请输入 Eagle 资料库根目录路径，或直接从 Eagle 软件窗口中拖入任意文件/图片后回车：")
            eagle_root = input().strip()
            
            print("\n请从 Eagle 软件中复制目录链接（可多选，用空格分隔），然后回车：")
            print("提示：在 Eagle 中右键点击目录，选择「复制链接」即可获取目录链接")
            folder_links = input().strip()
            
            # 设置环境变量
            os.environ["EAGLE_FOLDER_LINKS"] = folder_links
            
            # 调用 Eagle 重命名模块
            eagle_rename.main(eagle_root)
            
        elif choice == "3":
            print("\n感谢使用，再见！")
            break
            
        else:
            print("无效的选择，请重新输入！")

if __name__ == "__main__":
    main() 