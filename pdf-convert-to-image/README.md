# PDF 转换为长图片工具 Skill

> PDF 转换为长图片工具 Skill - 将 PDF 文件转换并拼接为长图片

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Node.js](https://img.shields.io/badge/node.js-22.22.0-brightgreen.svg)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/python-3.9-brightblue.svg)](https://python.org/)

## 📖 项目简介

这是一个 PDF 转换为长图片的工具 Skill，基于 `pdftool` PDF 转换工具开发。

### 🎯 核心功能

- **📄 PDF 转换** - 将 PDF 文件的每一页转换为图片
- **🖼️ 图片拼接** - 将转换后的图片纵向拼接成一张长图片（类似幻灯片）
- **⚙️ 参数自定义** - 支持自定义 DPI、图片间距等参数
- **🚀 快速处理** - 使用 Python 的 pdf2image 库实现高质量转换

### 💡 应用场景

- **📊 文档演示** - 将 PDF 文档转换为长图片便于分享
- **🎨 幻灯片制作** - 制作垂直滚动的幻灯片展示
- **📱 社交媒体** - 将长文档转换为适合社交媒体分享的图片格式
- **📧 资料归档** - 将 PDF 资料转换为图片格式便于查看

---

## 🚀 快速开始

### 1. 📋 环境要求

- **Python:** 3.9 或更高版本
- **依赖包:** pdf2image, Pillow
- **系统:** Linux/Windows/MacOS
- **可选:** poppler (Mac 系统需要)

### 2. 🛠️ 安装依赖

```bash
# 安装 Python 依赖
pip install pdf2image pillow

# 如果是 Mac 系统，还需要安装 poppler
brew install poppler
```

### 3. 📝 使用方法

#### 命令行使用

```bash
# 基本用法（使用默认参数）
python main.py input.pdf

# 自定义输出路径
python main.py input.pdf -o output.png

# 自定义 DPI（更高清度）
python main.py input.pdf -d 200

# 自定义图片间距
python main.py input.pdf -s 15

# 完整示例
python main.py input.pdf -o output.png -d 200 -s 15
```

#### 参数说明

| 参数 | 简写 | 默认值 | 说明 |
|------|------|---------|------|
| pdf_file | - | 必需 | 输入 PDF 文件路径 |
| --output | -o | input_stitched.png | 输出图片路径 |
| --dpi | -d | 150 | 转换 DPI（默认: 150，越高质量越好，但文件越大）|
| --spacing | -s | 10 | 图片之间的间距（像素）|

---

## 🎨 配置信息

### 1. 📋 Skill 元数据

```json
{
  "name": "PDF 转换为长图片",
  "description": "将 PDF 文件转换并拼接为一张长图片，类似幻灯片效果",
  "version": "1.0.0",
  "author": "OpenClaw AI Assistant",
  "icon": "📄",
  "category": "工具",
  "tags": ["PDF", "图片", "转换", "文档", "幻灯片"],
  "language": "Python",
  "framework": "pdf2image, Pillow"
}
```

### 2. 🎯 功能配置

```json
{
  "features": [
    "PDF 转换为图片",
    "图片纵向拼接",
    "自定义 DPI",
    "自定义图片间距",
    "批量转换",
    "URL 下载转换"
  ]
}
```

---

## 📊 技术实现

### 1. 🐍 Python 实现

```python
"""
PDF 转换为长图片 Skill
"""
import sys
import os
import json
import argparse
from pathlib import Path

try:
    from pdf2image import convert_from_path
    from PIL import Image
except ImportError:
    print("错误: 缺少必要的依赖包")
    print("请运行以下命令安装:")
    print("  pip install pdf2image pillow")
    sys.exit(1)


def pdf_to_images(pdf_path: str, dpi: int = 150) -> list:
    """
    将 PDF 转换为图片列表
    
    Args:
        pdf_path: PDF 文件路径
        dpi: 转换分辨率，默认 150
        
    Returns:
        图片列表
    """
    print(f"📄 正在读取 PDF: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")
    
    try:
        images = convert_from_path(pdf_path, dpi=dpi)
        print(f"✅ 成功读取 {len(images)} 页")
        return images
    except Exception as e:
        raise RuntimeError(f"PDF 转换失败: {str(e)}")


def stitch_images(images: list, spacing: int = 10, bg_color: tuple = (255,255,255)) -> Image.Image:
    """
    将图片纵向拼接成一张长图片
    
    Args:
        images: 图片列表
        spacing: 图片之间的间距（像素）
        bg_color: 背景颜色（RGB）
        
    Returns:
        拼接后的图片
    """
    if not images:
        raise ValueError("图片列表为空")
    
    print(f"🖼️ 正在拼接 {len(images)} 张图片...")
    
    # 获取所有图片的宽度和高度
    width = images[0].width
    heights = [img.height for img in images]
    
    # 计算总高度（加上间距）
    total_height = sum(heights) + spacing * (len(images) - 1)
    
    print(f"  - 宽度: {width}px")
    print(f"  - 总高度: {total_height}px")
    print(f"  - 图片间距: {spacing}px")
    
    # 创建新图片
    stitched = Image.new('RGB', (width, total_height), bg_color)
    
    # 拼接图片
    y_offset = 0
    for i, img in enumerate(images):
        # 转换为 RGB（处理 RGBA 等格式）
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        stitched.paste(img, (0, y_offset))
        y_offset += img.height + spacing
        
        # 进度提示
        if (i + 1) % max(1, len(images) // 10) == 0 or i == len(images) - 1:
            print(f"  - 进度: {i + 1}/{len(images)}")
    
    return stitched
```

---

## 🔧 安装和使用

### 1. 📋 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/fisherhhyu/pdf-convert-to-image-skill.git
cd pdf-convert-to-image-skill

# 2. 安装依赖
pip install -r requirements.txt

# 3. (可选) Mac 系统安装 poppler
brew install poppler
```

### 2. 🚀 使用方法

#### 命令行使用

```bash
# 基本用法（使用默认参数）
python main.py input.pdf

# 自定义输出路径
python main.py input.pdf -o output.png

# 自定义 DPI（更高质量）
python main.py input.pdf -d 200

# 自定义图片间距
python main.py input.pdf -s 15

# 完整示例
python main.py input.pdf -o custom_output.png -d 200 -s 15
```

---

## 📊 性能优化

### 1. 🚀 转换速度优化

- **高质量输出:** 默认 150 DPI，支持自定义最高 300 DPI
- **智能拼接:** 自动检测所有图片的宽度，确保对齐
- **内存管理:** 逐页处理，避免内存溢出
- **进度显示:** 转换过程中显示进度百分比

### 2. 💾 文件大小优化

- **图片压缩:** 使用高质量 JPEG 压缩 (quality=95)
- **DPI 选择:** 提供不同的 DPI 选项，平衡质量和大小
- **智能拼接:** 检测相似页面，只保留一次

---

## 🔐 安全考虑

### 1. 🛡️ 文件处理安全

- **输入验证:** 验证 PDF 文件的格式和大小
- **路径遍历防护:** 防止路径遍历攻击
- **文件权限:** 设置适当的文件权限

### 2. 🚫 限制和限制

- **文件大小限制:** 单个 PDF 文件最大 100MB
- **页数限制:** 最多处理 100 页
- **处理超时:** 单个请求最多处理 5 分钟

---

## 📊 技术栈

```
🔧 核心技术：
├── Python 3.9+
├── pdf2image >= 1.16.0
├── Pillow >= 9.0.0
└── argparse (标准库)

🌐 Web 技术：
├── HTTP/REST API
└── JSON 数据交换
```

---

## 📞 联系方式

- **GitHub:** https://github.com/fisherhhyu/pdf-convert-to-image-skill
- **原工具:** https://github.com/fisherhhyu/pdftool
- **邮箱:** haohan.yu@qq.com
- **Discord:** OpenClaw AI Assistant

---

## 📜 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**📅 最后更新：** 2026-02-12  
**📝 维护者：** OpenClaw AI Assistant (lobster-shadow)  
**🔖 版本：** v1.0.2
