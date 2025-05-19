# AI Image Batch Rename Tool

[English](README.md) | [中文](README_ZH.md)

An AI-powered image renaming tool that supports both local Ollama service and Silicon Flow API for image analysis and renaming.

## Features

- Supports multiple image formats (jpg, jpeg, png, gif, bmp, webp)
- Multiple renaming modes:
  - Override mode: Use AI-generated names directly
  - Prefix mode: Keep original filename with AI-generated name as prefix
  - Index mode: Add sequential numbers (001-999) to new names
- Batch processing support
- Real-time progress display
- Detailed error logging
- Support for both local Ollama service and Silicon Flow API

## System Requirements

- Python 3.8 or higher
- Windows operating system
- Ollama (if using Ollama service)

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. If using Ollama service:
   - Install Ollama (https://ollama.ai/)
   - Download required model:
     ```bash
     ollama pull qwen2.5vl:3b
     ```

4. If using Silicon Flow API:
   - Configure your API Key in `src/config.py`
   - Set `USE_OLLAMA` to `False`

## Usage

### Method 1: Using Batch File (Recommended)

1. Double-click to run `start.bat`
2. Select renaming mode from the menu:
   - [1] Override mode: Use new name directly
   - [2] Prefix mode: Keep original filename
   - [3] Add index: Add sequential numbers
   - [4] Exit program
3. Drag and drop image folder into the window, press Enter to start processing

### Method 2: Command Line

```bash
python src/main.py -i "image_folder_path" -m [override|prefix] -n
```

Parameters:
- `-i` or `--input_dir`: Input image folder path (required)
- `-m` or `--mode`: Renaming mode (optional)
  - `override`: Override mode (default)
  - `prefix`: Prefix mode
- `-n` or `--add_index`: Add sequential numbers (optional)

## Log Files

The program generates the following log files:
- `rename.log`: Main log file, records all operations
- `rename_failures.log`: Records failed renaming operations
- `token_usage.log`: Records token usage (only when using Silicon Flow API)

## Configuration

Configuration file is located at `src/config.py`, main settings include:

### General Settings
- `SUPPORTED_FORMATS`: Supported image formats
- `DEFAULT_MODE`: Default renaming mode
- `IMAGE_PROCESS_DELAY`: Delay between image processing
- `MAX_OUTPUT_TOKENS`: Output token limit

### API Settings
- `USE_OLLAMA`: Whether to use Ollama service
- `OLLAMA_MODEL`: Ollama model name
- `SILICON_FLOW_API_KEY`: Silicon Flow API key
- `SILICON_FLOW_MODEL`: Silicon Flow model name

## Notes

1. When using Ollama service:
   - Ensure Ollama service is running
   - Recommended to use local model for faster processing
   - No token usage limits

2. When using Silicon Flow API:
   - Valid API Key required
   - Be mindful of token usage limits
   - Adjust processing delay as needed

3. File naming:
   - Invalid characters are automatically removed
   - Timestamp is added if new filename already exists
   - Regular backups recommended

## Troubleshooting

1. If "Ollama service not running" error occurs:
   - Check if Ollama is properly installed
   - Manually start Ollama service: `ollama serve`

2. If processing is slow:
   - Check network connection
   - Adjust `IMAGE_PROCESS_DELAY` parameter
   - Consider using local Ollama service

3. If encoding errors occur:
   - Ensure system uses UTF-8 encoding
   - Check for special characters in filenames

## License

MIT License

## Chinese Documentation

For Chinese documentation, please see [README_CN.md](README_CN.md). 