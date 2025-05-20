# AI Smart Image Batch Rename Tool

[中文](README.md) | English

A powerful AI-driven image batch renaming tool that supports both regular folder mode and Eagle library specialized mode. Powered by Ollama local service or Silicon Flow API, it intelligently analyzes image content and generates content-appropriate filenames.

## Operation Modes

### 🖼 Regular Folder Mode
- Batch rename support for any local image folders
- Optional override mode or preserve original filename prefix
- Support for adding sequential numbers to prevent duplicates
- Preserve original file extensions

### 🦅 Eagle Professional Mode
- Process multiple Eagle directories simultaneously
- Smart directory hierarchy recognition with optional subdirectory inclusion
- Automatic synchronization of main images, thumbnails, and metadata files
- Complete error rollback mechanism for data safety
- Quick target folder location via Eagle folder links

## AI Engine Options

### Local Mode (Recommended)
- Uses Ollama local service
- Recommended model: qwen2.5vl:3b
- No internet required, fast processing, unlimited usage
- Ideal for large batch processing

### Online Mode
- Uses Silicon Flow API
- Requires API Key configuration
- Suitable for temporary use or when local service deployment is not possible

## Key Features

- 🤖 AI-powered image content analysis
- 📝 Intelligent filename generation based on content
- 🗂 Batch processing of specified folders and subfolders
- 🔄 Automatic handling of main images, thumbnails, and metadata
- 📊 Detailed operation logs and statistics
- 🛡 Robust error handling and rollback mechanism

## System Requirements

- Python 3.8 or higher
- Eagle 3.0 or higher
- Windows/macOS/Linux

## Installation

1. Clone or download this project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start Eagle software
2. Run the program:
```bash
python src/eagle_rename.py
```
3. Enter Eagle library path when prompted (drag and drop folder supported)
4. Input folder links to process (supports the following formats):
   - `eagle://folder/XXXXXXXX`
   - `http://localhost:41595/folder?id=XXXXXXXX`
   - Multiple folder links can be separated by spaces

## Features in Detail

### Smart Renaming
- AI-powered image content analysis
- Automatic content-based filename generation
- Duplicate name prevention
- File extension preservation

### Integrity Protection
- Synchronized updates for main images, thumbnails, and metadata
- Automatic rollback on errors
- File association integrity maintenance

### Logging
- Detailed operation logs
- Processing statistics
- Error tracking and diagnostics

## Important Notes

1. Ensure important data is backed up before use
2. Make sure Eagle software is running
3. Recommended to test with a small batch first
4. Do not manually modify files during processing

## FAQ

**Q: Why are some images skipped?**
A: Possible reasons include:
- File not in specified directory
- Unsupported file format
- File marked as deleted
- AI analysis failure

**Q: What image formats are supported?**
A: Supports common image formats supported by Eagle, including:
- JPG/JPEG
- PNG
- WebP
- GIF
etc.

---
@  shichaoooooo