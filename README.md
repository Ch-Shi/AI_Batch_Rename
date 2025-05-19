# 批量图像智能重命名工具

这是一个基于 AI 的批量图像重命名工具，可以自动分析图像内容并生成合适的中文名称。该工具支持使用本地的 Ollama 服务或硅基流动 API 来理解图像内容，并生成描述性的文件名。

## 功能特点

- 支持批量处理图像文件
- 递归扫描子目录
- 支持多种命名策略（覆盖原名/保留前缀）
- 可选的序号添加功能
- 详细的日志记录
- 支持多种图像格式
- 支持本地 Ollama 服务和硅基流动 API

## 安装步骤

1. 克隆仓库：
```bash
git clone [仓库地址]
cd [仓库目录]
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 安装 Ollama（如果使用本地 Ollama 服务）：
   - 访问 [Ollama 官网](https://ollama.com) 下载并安装 Ollama
   - 拉取 Qwen2.5VL-7B 模型：
   ```bash
   ollama pull qwen2.5vl:7b
   ```

4. 配置 API 密钥（如果使用硅基流动 API）：
在 `src/config.py` 中设置您的 API 密钥：
```python
API_KEY = "您的API密钥"
```

## 使用方法

### 基本用法

```bash
python src/main.py -i <图像目录路径> [-m <命名策略>] [-n]
```

### 参数说明

- `-i, --input_dir`：必填。指定要批量处理的图像所在目录路径。脚本会递归扫描该目录下的所有子文件夹，找到符合支持格式的图像文件。

- `-m, --mode`：可选。指定命名策略，可选值为：
  - `override`：使用模型生成的新名称直接作为文件的新名字
  - `prefix`：保留原文件名前缀，并在其后附加模型生成的新名称
  - 不指定时使用配置文件中的默认策略

- `-n, --add_index`：可选。添加此参数时，将在生成的文件名末尾增加编号序号（从1开始递增的三位数字）。

### 配置说明

在 `src/config.py` 中可以配置以下选项：

```python
# 选择使用的 AI 服务
USE_OLLAMA = True  # True 使用本地 Ollama，False 使用硅基流动 API

# Ollama 配置
OLLAMA_BASE_URL = "http://localhost:11434"  # Ollama 服务地址
OLLAMA_MODEL = "qwen2.5vl:7b"  # 使用的 Ollama 模型

# 文件处理配置
SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
DEFAULT_MODE = 'override'  # 默认命名策略
ADD_INDEX = False  # 是否添加序号
```

### 命名策略示例

1. 覆盖原名模式：
   - 原文件：`IMG001.jpg`
   - 新文件：`夕阳.jpg`

2. 保留前缀模式：
   - 原文件：`IMG001.jpg`
   - 新文件：`IMG001_夕阳.jpg`

3. 添加编号：
   - 原文件：`IMG001.jpg`
   - 新文件：`夕阳001.jpg` 或 `IMG001_夕阳001.jpg`

### 使用示例

1. 使用默认配置（覆盖原名，不添加编号）：
```bash
python src/main.py -i photos/
```

2. 使用保留前缀模式并添加编号：
```bash
python src/main.py -i photos/ -m prefix -n
```

## 日志说明

脚本会在控制台输出日志，并同时将日志写入 `rename.log` 文件。日志包含：
- 处理开始和结束信息
- 每个文件的处理结果
- 错误信息和原因
- 成功和失败的数量统计

示例日志：
```
2025-05-18 00:50:00 [INFO] 开始处理目录: photos/, 策略: prefix, 添加编号: True
2025-05-18 00:50:01 [INFO] [1/10] 重命名成功: IMG_0001.png -> IMG_0001_花海001.png
2025-05-18 00:50:03 [INFO] [2/10] 重命名成功: IMG_0002.png -> IMG_0002_青山002.png
2025-05-18 00:50:10 [ERROR] [3/10] 重命名失败: IMG_0003.png - 错误: API 请求失败，状态码: 500
2025-05-18 00:50:15 [INFO] 处理完成。成功: 9 张, 失败: 1 张。
```

## 注意事项

1. 如果使用本地 Ollama 服务：
   - 确保 Ollama 服务已启动
   - 确保已下载所需的模型
   - 确保 Ollama 服务地址配置正确

2. 如果使用硅基流动 API：
   - 确保有稳定的网络连接
   - 正确配置 API 密钥

3. 其他注意事项：
   - 处理大量图片时可能需要较长时间，请耐心等待
   - 建议在处理重要文件前先进行测试
   - 如遇到问题，请查看日志文件了解详细信息

## 项目结构

```
批量重命名/
├── requirements.txt
└── src/
    ├── config.py
    ├── main.py
    ├── core/
    │   ├── ai_client.py
    │   ├── naming.py
    │   └── image_utils.py
    └── utils/
        └── logger.py
```

## 许可证

[添加许可证信息]

## 贡献

欢迎提交 Issue 和 Pull Request！ 