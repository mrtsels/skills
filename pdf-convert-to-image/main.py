#!/usr/bin/env python3
"""
PDF 转换为长图片 Skill 主程序
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


class PDFConvertSkill:
    """PDF 转换为长图片 Skill"""
    
    def __init__(self):
        self.name = "PDF 转换为长图片"
        self.version = "1.0.0"
        self.description = "将 PDF 文件转换并拼接为一张长图片，类似幻灯片效果"
    
    def convert_pdf(self, pdf_path, output_path=None, dpi=150, spacing=10):
        """
        转换 PDF 为长图片
        
        Args:
            pdf_path: PDF 文件路径
            output_path: 输出图片路径
            dpi: 转换 DPI，默认 150
            spacing: 图片间距
            
        Returns:
            结果字典
        """
        print(f"📄 正在转换 PDF: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            return {
                "success": False,
                "error": f"PDF 文件不存在: {pdf_path}"
            }
        
        try:
            # 转换 PDF 为图片
            images = convert_from_path(pdf_path, dpi=dpi)
            stitched_image = self.stitch_images(images, spacing=spacing)
            
            # 确定输出路径
            if output_path:
                output_path = Path(output_path)
            else:
                input_path = Path(pdf_path)
                output_path = input_path.parent / f"{input_path.stem}_stitched.png"
            
            # 保存图片
            print(f"💾 正在保存图片到: {output_path}")
            stitched_image.save(output_path, quality=95)
            
            # 获取文件大小
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            file_size_str = f"{file_size_mb:.2f} MB" if file_size_mb >= 1 else f"{file_size_mb * 1024:.0f} KB"
            
            return {
                "success": True,
                "output_path": str(output_path.absolute()),
                "file_size_mb": file_size_mb,
                "file_size_str": file_size_str,
                "pages": len(images),
                "width": images[0].width if images else 0,
                "height": sum([img.height for img in images]) + spacing * (len(images) - 1) if images else 0
            }
            
        except Exception as e:
            print(f"❌ 转换失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def convert_pdf_from_url(self, pdf_url, output_path=None, dpi=150, spacing=10):
        """
        从 URL 下载并转换 PDF
        
        Args:
            pdf_url: PDF 文件 URL
            output_path: 输出图片路径
            dpi: 转换 DPI，默认 150
            spacing: 图片间距
            
        Returns:
            结果字典
        """
        print(f"📥 正在下载 PDF: {pdf_url}")
        
        try:
            import requests
            
            # 下载 PDF
            response = requests.get(pdf_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # 保存临时 PDF 文件
            temp_pdf = Path(__file__).parent / "temp.pdf"
            with open(temp_pdf, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"✅ PDF 下载完成: {temp_pdf}")
            
            # 转换 PDF
            result = self.convert_pdf(str(temp_pdf), output_path, dpi, spacing)
            
            # 删除临时文件
            os.remove(temp_pdf)
            print(f"🗑️ 临时文件已删除: {temp_pdf}")
            
            return result
            
        except Exception as e:
            print(f"❌ 下载或转换失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def stitch_images(self, images, spacing=10, bg_color=(255,255,255)):
        """
        将图片纵向拼接成一张长图片
        
        Args:
            images: 图片列表
            spacing: 图片间距
            bg_color: 背景颜色
            
        Returns:
            拼接后的图片
        """
        if not images:
            raise ValueError("图片列表为空")
        
        print(f"🖼️ 正在拼接 {len(images)} 张图片...")
        
        # 获取所有图片的宽度和高度
        width = images[0].width
        heights = [img.height for img in images]
        
        # 计算总高度（包括间距）
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
    
    def batch_convert(self, pdf_dir, output_dir=None, dpi=150, spacing=10):
        """
        批量转换目录中的 PDF 文件
        
        Args:
            pdf_dir: PDF 文件目录
            output_dir: 输出图片目录
            dpi: 转换 DPI
            spacing: 图片间距
            
        Returns:
            结果列表
        """
        print(f"📁 正在批量转换目录: {pdf_dir}")
        
        pdf_dir = Path(pdf_dir)
        if not pdf_dir.exists():
            return {
                "success": False,
                "error": f"目录不存在: {pdf_dir}"
            }
        
        # 查找所有 PDF 文件
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            return {
                "success": False,
                "error": f"目录中没有找到 PDF 文件: {pdf_dir}"
            }
        
        print(f"📊 找到 {len(pdf_files)} 个 PDF 文件")
        
        # 确定输出目录
        if output_dir:
            output_dir = Path(output_dir)
        else:
            output_dir = pdf_dir / "converted"
        
        output_dir.mkdir(exist_ok=True)
        
        # 批量转换
        results = []
        success_count = 0
        fail_count = 0
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n[{i}/{len(pdf_files)}] 处理: {pdf_file.name}")
            
            output_file = output_dir / f"{pdf_file.stem}_stitched.png"
            result = self.convert_pdf(str(pdf_file), str(output_file), dpi, spacing)
            
            results.append({
                "file": pdf_file.name,
                "result": result
            })
            
            if result.get('success'):
                success_count += 1
            else:
                fail_count += 1
        
        print(f"\n✅ 批量转换完成!")
        print(f"   成功: {success_count}")
        print(f"   失败: {fail_count}")
        
        return {
            "success": True,
            "total": len(pdf_files),
            "success_count": success_count,
            "fail_count": fail_count,
            "results": results
        }
    
    def get_skill_info(self):
        """
        获取 Skill 信息
        
        Returns:
            Skill 信息字典
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": "OpenClaw AI Assistant",
            "icon": "📄",
            "category": "工具",
            "tags": ["PDF", "图片", "转换", "文档", "幻灯片"],
            "language": "Python",
            "framework": "pdf2image, Pillow",
            "features": [
                "PDF 转换为图片",
                "图片纵向拼接",
                "自定义 DPI",
                "自定义图片间距",
                "批量转换",
                "URL 下载转换"
            ]
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='PDF 转换为长图片 Skill',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 单文件转换参数
    parser.add_argument('pdf_file', nargs='?', help='PDF 文件路径')
    parser.add_argument('-o', '--output', help='输出图片路径 (默认: input_stitched.png)')
    parser.add_argument('-d', '--dpi', type=int, default=150, help='转换 DPI (默认: 150)')
    parser.add_argument('-s', '--spacing', type=int, default=10, help='图片间距 (像素, 默认: 10)')
    
    # URL 转换参数
    parser.add_argument('-u', '--url', help='PDF 文件 URL')
    
    # 批量转换参数
    parser.add_argument('-b', '--batch', action='store_true', help='批量转换模式')
    parser.add_argument('--pdf-dir', help='PDF 文件目录 (批量转换模式)')
    parser.add_argument('--output-dir', help='输出图片目录 (批量转换模式)')
    
    # Skill 信息参数
    parser.add_argument('--skill-info', action='store_true', help='显示 Skill 信息')
    
    # 帮助参数
    parser.add_argument('-h', '--help', action='store_true', help='显示帮助信息')
    
    args = parser.parse_args()
    
    # 创建 Skill 实例
    skill = PDFConvertSkill()
    
    # 显示 Skill 信息
    if args.skill_info:
        info = skill.get_skill_info()
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return
    
    # 显示帮助
    if args.help or (not args.pdf_file and not args.url):
        print(f"""
📄 PDF 转换为长图片 Skill v{skill.version}

{skill.description}

🚀 快速使用:
    # 单文件转换
    python main.py input.pdf
    
    # 自定义输出
    python main.py input.pdf -o output.png -d 200 -s 15
    
    # URL 下载转换
    python main.py -u https://example.com/document.pdf
    
    # 批量转换
    python main.py -b --pdf-dir ./pdfs --output-dir ./output

📋 选项:
    pdf_file             PDF 文件路径
    -o, --output         输出图片路径 (默认: input_stitched.png)
    -d, --dpi             转换 DPI (默认: 150)
    -s, --spacing         图片间距 (像素, 默认: 10)
    -u, --url             PDF 文件 URL
    -b, --batch           批量转换模式
    --pdf-dir             PDF 文件目录 (批量转换模式)
    --output-dir           输出目录 (批量转换模式)
    --skill-info           显示 Skill 信息
    -h, --help            显示此帮助信息

💡 使用示例:
    # 基本转换
    python main.py document.pdf
    
    # 高质量转换
    python main.py document.pdf -d 200 -s 15
    
    # URL 下载转换
    python main.py -u https://example.com/doc.pdf -o output.png
    
    # 批量转换
    python main.py -b --pdf-dir ./pdfs --output-dir ./output

📖 工具源码: https://github.com/fisherhhyu/pdftool
🤖 Skill 作者: OpenClaw AI Assistant (lobster-shadow)
        """)
        return
    
    # 单文件转换
    if args.pdf_file and not args.batch:
        result = skill.convert_pdf(args.pdf_file, args.output, args.dpi, args.spacing)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    
    # URL 下载转换
    if args.url:
        result = skill.convert_pdf_from_url(args.url, args.output, args.dpi, args.spacing)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    
    # 批量转换
    if args.batch and args.pdf_dir:
        result = skill.batch_convert(args.pdf_dir, args.output_dir, args.dpi, args.spacing)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    
    print("❌ 请指定操作参数，使用 -h 查看帮助信息")


if __name__ == '__main__':
    main()
