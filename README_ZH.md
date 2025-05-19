# 图像智能重命名工具

[English](README.md) | [中文](README_ZH.md)

这是一个基于 AI 的图像智能重命名工具，支持使用本地 Ollama 服务或硅基流动 API 来分析和重命名图片。

## 功能特点

- 支持多种图片格式（jpg, jpeg, png, gif, bmp, webp）
- 提供多种重命名模式：
  - 覆盖模式：直接使用 AI 生成的新名称
  - 前缀模式：保留原文件名，添加 AI 生成的新名称
  - 序号模式：新名称后添加序号（001-999）
- 支持批量处理
- 实时显示处理进度
- 详细的错误日志记录
- 支持本地 Ollama 服务和硅基流动 API

## 系统要求

- Python 3.8 或更高版本
- Windows 操作系统
- 如果使用 Ollama 服务，需要安装 Ollama

## 安装步骤

1. 克隆或下载本项目到本地

2. 安装依赖包：
```bash
pip install -r requirements.txt
```

3. 如果使用 Ollama 服务：
   - 安装 Ollama（https://ollama.ai/）
   - 下载所需模型：
     ```bash
     ollama pull qwen2.5vl:3b
     ```

4. 如果使用硅基流动 API：
   - 在 `src/config.py` 中配置您的 API Key
   - 将 `USE_OLLAMA` 设置为 `False`

## 使用方法

### 方法一：使用批处理文件（推荐）

1. 双击运行 `start.bat`
2. 在菜单中选择重命名模式：
   - [1] 覆盖模式：直接使用新名称
   - [2] 前缀模式：保留原文件名
   - [3] 添加序号：新名称后添加序号
   - [4] 退出程序
3. 将图片文件夹拖放到窗口中，按回车开始处理

### 方法二：命令行方式

```bash
python src/main.py -i "图片文件夹路径" -m [override|prefix] -n
```

参数说明：
- `-i` 或 `--input_dir`：指定输入图片文件夹路径（必需）
- `-m` 或 `--mode`：选择重命名模式（可选）
  - `override`：覆盖模式（默认）
  - `prefix`：前缀模式
- `-n` 或 `--add_index`：添加序号（可选）

## 日志文件

程序会生成以下日志文件：
- `rename.log`：主日志文件，记录所有操作
- `rename_failures.log`：记录重命名失败的文件信息
- `token_usage.log`：记录 token 使用情况（仅在使用硅基流动 API 时）

## 配置说明

配置文件位于 `src/config.py`，主要配置项包括：

### 通用配置
- `SUPPORTED_FORMATS`：支持的图片格式
- `DEFAULT_MODE`：默认重命名模式
- `IMAGE_PROCESS_DELAY`：图片处理间隔时间
- `MAX_OUTPUT_TOKENS`：输出 token 限制

### API 配置
- `USE_OLLAMA`：是否使用 Ollama 服务
- `OLLAMA_MODEL`：Ollama 模型名称
- `SILICON_FLOW_API_KEY`：硅基流动 API 密钥
- `SILICON_FLOW_MODEL`：硅基流动模型名称

## 注意事项

1. 使用 Ollama 服务时：
   - 确保 Ollama 服务已启动
   - 建议使用本地模型以获得更快的处理速度
   - 没有 token 使用限制

2. 使用硅基流动 API 时：
   - 需要有效的 API Key
   - 注意 token 使用限制
   - 建议适当调整处理间隔时间

3. 文件命名：
   - 新文件名会自动去除非法字符
   - 如果新文件名已存在，会自动添加时间戳
   - 建议定期备份重要文件

## 常见问题

1. 如果遇到 "Ollama 服务未启动" 错误：
   - 检查 Ollama 是否正确安装
   - 手动启动 Ollama 服务：`ollama serve`

2. 如果处理速度较慢：
   - 检查网络连接
   - 调整 `IMAGE_PROCESS_DELAY` 参数
   - 考虑使用本地 Ollama 服务

3. 如果出现编码错误：
   - 确保系统使用 UTF-8 编码
   - 检查文件名是否包含特殊字符

## 许可证

MIT License 