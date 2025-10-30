#!/usr/bin/env python3
"""
生成Word文档 - 功能点列表和截图
"""

import os
import json
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

def create_function_document():
    """创建功能点文档"""
    
    # 读取报告数据
    with open('/workspace/screenshots_full/report.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    screenshots = data['screenshots']
    
    # 创建Word文档
    doc = Document()
    
    # 设置默认中文字体
    doc.styles['Normal'].font.name = 'Microsoft YaHei'
    doc.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    
    # 添加标题
    title = doc.add_heading('海星育后台管理系统功能截图文档', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 添加基本信息
    info_para = doc.add_paragraph()
    info_para.add_run('系统地址：').bold = True
    info_para.add_run('https://jhtest.bjstarfish.com/\n')
    info_para.add_run('生成时间：').bold = True
    info_para.add_run(f'{data.get("base_url", "")}\n')
    info_para.add_run('总功能点数：').bold = True
    info_para.add_run(f'{len(screenshots)} 个')
    
    doc.add_paragraph()  # 空行
    
    # 创建表格（2列：功能点描述 + 截图）
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Light Grid Accent 1'
    
    # 设置表头
    header_cells = table.rows[0].cells
    header_cells[0].text = '功能点描述'
    header_cells[1].text = '功能截图'
    
    # 设置表头样式
    for cell in header_cells:
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(12)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        # 设置背景色
        shading_elm = cell._element.get_or_add_tcPr()
        shading = shading_elm.get_or_add_shd()
        shading.set(qn('w:fill'), '4472C4')  # 蓝色背景
    
    # 添加数据行
    print("正在生成Word文档...")
    for i, screenshot in enumerate(screenshots, 1):
        print(f"  处理 [{i}/{len(screenshots)}]: {screenshot['name']}")
        
        # 添加新行
        row_cells = table.add_row().cells
        
        # 第一列：功能点描述
        desc_paragraph = row_cells[0].paragraphs[0]
        
        # 序号
        run = desc_paragraph.add_run(f"{screenshot['index']}. ")
        run.font.bold = True
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(68, 114, 196)
        
        # 功能名称
        run = desc_paragraph.add_run(f"{screenshot['name']}\n\n")
        run.font.size = Pt(10)
        run.font.bold = True
        
        # 页面标题
        run = desc_paragraph.add_run(f"页面标题：{screenshot['title']}\n")
        run.font.size = Pt(9)
        
        # URL
        run = desc_paragraph.add_run(f"URL：{screenshot['url']}")
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(128, 128, 128)
        
        # 设置垂直居中
        row_cells[0].vertical_alignment = 1  # 居中
        
        # 第二列：截图
        img_path = os.path.join('/workspace/screenshots_full', screenshot['filename'])
        
        if os.path.exists(img_path):
            # 添加图片到单元格
            paragraph = row_cells[1].paragraphs[0]
            run = paragraph.add_run()
            
            # 设置图片宽度（单元格宽度）
            try:
                run.add_picture(img_path, width=Inches(4.5))
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            except Exception as e:
                paragraph.add_run(f"[图片加载失败: {str(e)}]")
        else:
            row_cells[1].text = '[图片文件不存在]'
        
        # 设置行高
        row_cells[0].width = Inches(2.5)
        row_cells[1].width = Inches(4.5)
    
    # 保存文档
    output_path = '/workspace/海星育后台管理系统功能截图文档.docx'
    doc.save(output_path)
    
    print(f"\n✓ Word文档已生成: {output_path}")
    print(f"✓ 包含 {len(screenshots)} 个功能点")
    
    return output_path


if __name__ == '__main__':
    create_function_document()
