# AI 智能图片批量重命名工具

中文 | [English](README_EN.md)

一款强大的 AI 驱动的图片批量重命名工具，支持普通文件夹模式和 Eagle 资源库专用模式。基于 Ollama 本地服务或硅基流动 API，智能分析图片内容并生成贴合内容的文件名。

## 运行模式

### 🖼 普通文件夹模式
- 支持任意本地图片文件夹的批量重命名
- 可选择覆盖模式或保留原文件名前缀
- 支持添加序号，避免重名
- 保持原始文件扩展名不变

### 🦅 Eagle 专业模式
- 支持多个 Eagle 目录同时处理
- 智能识别目录层级关系，可选择是否包含子目录
- 自动处理主图、缩略图和元数据文件的同步更新
- 完整的错误回滚机制，确保数据安全
- 支持通过 Eagle 文件夹链接快速定位目标文件夹

## AI 引擎选择

### 本地模式（推荐）
- 使用 Ollama 本地服务
- 推荐模型：qwen2.5vl:3b
- 无需联网，速度快，无次数限制
- 适合大批量处理

### 在线模式
- 使用硅基流动 API
- 需要配置 API Key
- 适合临时使用或无法部署本地服务的场景

## 主要功能

- 🤖 基于 AI 的图片内容分析
- 📝 智能生成符合内容的文件名
- 🗂 支持批量处理指定文件夹及其子文件夹
- 🔄 自动处理主图、缩略图和元数据文件
- 📊 详细的操作日志和统计信息
- 🛡 完善的错误处理和回滚机制

## 系统要求

- Python 3.8 或更高版本
- Eagle 3.0 或更高版本
- Windows/macOS/Linux

## 安装说明

1. 克隆或下载本项目到本地
2. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 启动 Eagle 软件
2. 运行程序：
```bash
python src/eagle_rename.py
```
3. 按提示输入 Eagle 资料库路径（可直接拖入文件夹）
4. 输入要处理的文件夹链接（支持以下格式）：
   - `eagle://folder/XXXXXXXX`
   - `http://localhost:41595/folder?id=XXXXXXXX`
   - 多个文件夹链接可用空格分隔

## 功能特点

### 智能重命名
- 使用 AI 分析图片内容
- 自动生成符合内容的文件名
- 避免重复名称
- 保持文件扩展名不变

### 完整性保护
- 同步更新主图、缩略图和元数据
- 出错时自动回滚所有更改
- 保持文件关联完整性

### 日志记录
- 详细的操作日志
- 处理统计信息
- 错误追踪和诊断

## 注意事项

1. 使用前请确保已备份重要数据
2. 确保 Eagle 软件处于运行状态
3. 建议先在小范围测试后再进行大批量处理
4. 处理过程中请勿手动修改相关文件

## 常见问题

**Q: 为什么有些图片被跳过了？**
A: 可能的原因包括：
- 文件不在指定目录中
- 文件格式不受支持
- 文件已被标记为删除
- AI 分析失败

**Q: 支持哪些图片格式？**
A: 支持 Eagle 支持的常见图片格式，包括：
- JPG/JPEG
- PNG
- WebP
- GIF
等

---
@  shichaoooooo