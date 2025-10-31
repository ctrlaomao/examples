#!/usr/bin/env python3
"""
票务系统增强版截图工具 - 深度遍历所有功能
"""

import os
import time
import json
import hashlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

class EnhancedTicketSystemScreenshotter:
    def __init__(self, base_url, username, password, output_dir="screenshots_ticket_system_enhanced"):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.output_dir = output_dir
        self.screenshots = []
        self.visited_urls = set()
        self.screenshot_index = 1
        
        os.makedirs(output_dir, exist_ok=True)
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--lang=zh-CN')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(5)
        
    def login(self):
        """登录"""
        print(f"\n正在登录票务系统...")
        self.driver.get(self.base_url)
        time.sleep(5)
        
        try:
            self.save_screenshot("系统登录", "登录页面", "票务系统登录界面")
            
            # 输入用户名
            username_input = self.driver.find_element(By.XPATH, "//input[@type='text']")
            password_input = self.driver.find_element(By.XPATH, "//input[@type='password']")
            
            username_input.send_keys(self.username)
            password_input.send_keys(self.password)
            
            login_button = self.driver.find_element(By.XPATH, "//button")
            login_button.click()
            
            # 等待登录
            time.sleep(8)
            
            print(f"✓ 登录成功，当前URL: {self.driver.current_url}")
            
            # 主页截图
            self.save_screenshot("系统主页", "Dashboard主页", "登录后首页")
            
            return True
        except Exception as e:
            print(f"✗ 登录失败: {str(e)}")
            return False
    
    def save_screenshot(self, module, function, description):
        """保存截图"""
        try:
            current_url = self.driver.current_url
            if current_url in self.visited_urls:
                return False
            
            self.visited_urls.add(current_url)
            
            time.sleep(2)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in f"{module}_{function}")
            safe_name = safe_name[:70]
            
            filename = f"{self.screenshot_index:04d}_{safe_name}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            self.driver.save_screenshot(filepath)
            
            self.screenshots.append({
                "index": self.screenshot_index,
                "module": module,
                "function": function,
                "description": description,
                "filename": filename,
                "url": current_url,
                "title": self.driver.title
            })
            
            print(f"  [{self.screenshot_index:04d}] ✓ {module} - {function}")
            self.screenshot_index += 1
            return True
        except Exception as e:
            print(f"  ✗ 截图失败: {str(e)}")
            return False
    
    def find_all_clickable_elements(self):
        """查找所有可点击元素"""
        clickables = []
        try:
            # 查找所有可能可点击的元素
            elements = self.driver.find_elements(By.XPATH,
                "//a | //button | //*[@onclick] | //*[contains(@class, 'clickable')] | //*[contains(@class, 'link')]")
            
            for elem in elements:
                try:
                    if elem.is_displayed() and elem.is_enabled():
                        text = elem.text.strip()
                        if text and len(text) < 100:
                            clickables.append({
                                'element': elem,
                                'text': text,
                                'tag': elem.tag_name
                            })
                except:
                    pass
            
            return clickables
        except:
            return []
    
    def explore_deeply(self):
        """深度探索系统"""
        print("\n" + "=" * 80)
        print("开始深度遍历票务系统...")
        print("=" * 80)
        
        # 等待页面完全加载
        time.sleep(5)
        
        # 记录初始URL
        initial_url = self.driver.current_url
        
        # 查找所有可点击元素
        print("\n正在查找所有可点击元素...")
        clickables = self.find_all_clickable_elements()
        print(f"✓ 发现 {len(clickables)} 个可点击元素\n")
        
        # 过滤出看起来像菜单的元素
        menu_items = []
        button_items = []
        
        for item in clickables:
            text = item['text']
            # 跳过一些明显不是菜单的项
            if text in ['EN', 'CN', '登出', '退出']:
                continue
            
            if item['tag'] == 'a' or 'menu' in item['element'].get_attribute('class').lower():
                menu_items.append(item)
            else:
                button_items.append(item)
        
        print(f"识别出菜单项: {len(menu_items)} 个")
        print(f"识别出按钮: {len(button_items)} 个\n")
        
        # 遍历菜单项
        for i, menu_item in enumerate(menu_items, 1):
            try:
                print(f"\n{'='*80}")
                print(f"[{i}/{len(menu_items)}] 点击菜单: {menu_item['text']}")
                print(f"{'='*80}")
                
                # 返回主页
                if self.driver.current_url != initial_url:
                    self.driver.get(initial_url)
                    time.sleep(3)
                
                # 重新查找该菜单项
                time.sleep(1)
                fresh_clickables = self.find_all_clickable_elements()
                target = None
                for fc in fresh_clickables:
                    if fc['text'] == menu_item['text']:
                        target = fc['element']
                        break
                
                if target:
                    # 点击菜单
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target)
                        time.sleep(0.5)
                        target.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", target)
                    
                    time.sleep(3)
                    
                    # 截图
                    module_name = menu_item['text']
                    self.save_screenshot(module_name, f"{module_name}页面", f"{module_name}功能页面")
                    
                    # 查找该页面的操作按钮
                    print(f"  → 查找页面操作按钮...")
                    page_buttons = self.find_all_clickable_elements()
                    
                    # 过滤出操作按钮
                    operation_keywords = ['新增', '新建', '添加', '创建', '编辑', '修改', 
                                        '查看', '详情', '删除', '设置', '导出', '导入']
                    
                    operation_buttons = []
                    for pb in page_buttons:
                        if any(keyword in pb['text'] for keyword in operation_keywords):
                            operation_buttons.append(pb)
                    
                    print(f"  → 发现操作按钮: {len(operation_buttons)} 个")
                    
                    # 点击每个操作按钮
                    for j, op_btn in enumerate(operation_buttons[:5], 1):  # 限制5个
                        try:
                            print(f"    [{j}] 点击: {op_btn['text']}")
                            
                            # 重新查找按钮
                            time.sleep(1)
                            fresh_buttons = self.find_all_clickable_elements()
                            target_btn = None
                            for fb in fresh_buttons:
                                if fb['text'] == op_btn['text']:
                                    target_btn = fb['element']
                                    break
                            
                            if target_btn:
                                try:
                                    target_btn.click()
                                except:
                                    self.driver.execute_script("arguments[0].click();", target_btn)
                                
                                time.sleep(2)
                                
                                # 截图
                                function_name = f"{module_name} - {op_btn['text']}"
                                self.save_screenshot(module_name, function_name, f"{op_btn['text']}功能")
                                
                                # 尝试关闭弹窗或返回
                                try:
                                    close_btn = self.driver.find_element(By.XPATH, 
                                        "//*[contains(@class, 'close')] | //button[contains(text(), '取消')]")
                                    close_btn.click()
                                    time.sleep(1)
                                except:
                                    if self.driver.current_url != initial_url:
                                        self.driver.back()
                                        time.sleep(2)
                        except Exception as e:
                            print(f"    ✗ 处理按钮出错: {str(e)}")
                
                print()
            except Exception as e:
                print(f"✗ 处理菜单出错: {str(e)}\n")
        
        print("=" * 80)
        print(f"✓ 遍历完成！共截图 {len(self.screenshots)} 个功能点")
        print("=" * 80)
    
    def close(self):
        if self.driver:
            self.driver.quit()


def create_word_doc(screenshots, output_path):
    """生成Word文档"""
    print("\n正在生成Word文档...")
    
    doc = Document()
    doc.styles['Normal'].font.name = 'Microsoft YaHei'
    doc.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    
    title = doc.add_heading('票务系统 - 完整功能截图文档', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    info = doc.add_paragraph()
    info.add_run('系统名称：').bold = True
    info.add_run('票务系统\n')
    info.add_run('生成时间：').bold = True
    info.add_run(f'{time.strftime("%Y-%m-%d %H:%M:%S")}\n')
    info.add_run('截图总数：').bold = True
    info.add_run(f'{len(screenshots)} 张')
    
    doc.add_paragraph()
    
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    
    header = table.rows[0].cells
    header[0].text = '序号'
    header[1].text = '功能点'
    header[2].text = '截图'
    
    for cell in header:
        for para in cell.paragraphs:
            for run in para.runs:
                run.font.bold = True
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    widths = (Inches(0.5), Inches(2.5), Inches(4.0))
    for row in table.rows:
        for idx, width in enumerate(widths):
            row.cells[idx].width = width
    
    for ss in screenshots:
        row = table.add_row()
        cells = row.cells
        
        for idx, width in enumerate(widths):
            cells[idx].width = width
        
        cells[0].text = str(ss['index'])
        cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        desc_para = cells[1].paragraphs[0]
        run = desc_para.add_run(f"【{ss['module']}】\n")
        run.font.bold = True
        
        run = desc_para.add_run(f"{ss['function']}\n\n")
        run.font.size = Pt(9)
        
        run = desc_para.add_run(f"{ss['description']}")
        run.font.size = Pt(8)
        
        img_path = os.path.join('/workspace/screenshots_ticket_system_enhanced', ss['filename'])
        if os.path.exists(img_path):
            img_para = cells[2].paragraphs[0]
            img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            try:
                run = img_para.add_run()
                run.add_picture(img_path, width=Inches(3.8))
            except:
                img_para.add_run('[图片失败]')
    
    doc.save(output_path)
    print(f"✓ Word文档: {output_path} ({os.path.getsize(output_path) / 1024 / 1024:.2f} MB)")


def main():
    base_url = "https://xstest.axioxio.com/"
    username = "13811458301"
    password = "4<z%0/RS"
    
    print("=" * 80)
    print("票务系统增强版截图工具")
    print("=" * 80)
    
    screenshotter = None
    try:
        screenshotter = EnhancedTicketSystemScreenshotter(base_url, username, password)
        
        if screenshotter.login():
            screenshotter.explore_deeply()
            
            # 生成Word
            doc_path = '/workspace/票务系统完整截图文档（增强版）.docx'
            create_word_doc(screenshotter.screenshots, doc_path)
            
            # 打包
            print("\n正在打包...")
            os.system("cd /workspace && zip -q -r 票务系统完整截图包（增强版）.zip screenshots_ticket_system_enhanced/ 票务系统完整截图文档（增强版）.docx")
            
            print("\n" + "=" * 80)
            print("✅ 完成！")
            print(f"📊 截图: {len(screenshotter.screenshots)} 张")
            print(f"📄 Word: {doc_path}")
            print(f"📦 压缩包: /workspace/票务系统完整截图包（增强版）.zip")
            print("=" * 80)
    
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if screenshotter:
            screenshotter.close()


if __name__ == "__main__":
    main()
