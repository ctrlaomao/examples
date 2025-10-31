#!/usr/bin/env python3
"""
票务系统完整截图工具 - 包含子菜单
"""

import os
import time
import json
import hashlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn


class TicketSystemCompleteScreenshotter:
    def __init__(self, base_url, username, password, output_dir="screenshots_ticket_complete"):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.output_dir = output_dir
        self.screenshots = []
        self.visited_states = set()
        self.screenshot_index = 1
        
        os.makedirs(output_dir, exist_ok=True)
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--ignore-certificate-errors')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(2)
    
    def get_page_state_hash(self):
        """获取页面状态哈希（用于去重）"""
        try:
            url = self.driver.current_url
            body_text = self.driver.find_element(By.TAG_NAME, "body").text[:500]
            state = f"{url}_{body_text}"
            return hashlib.md5(state.encode()).hexdigest()
        except:
            return None
    
    def login(self):
        """登录"""
        print(f"\n正在登录票务系统...")
        self.driver.get(self.base_url)
        time.sleep(5)
        
        try:
            # 切换到简体中文
            print("  → 切换到简体中文...")
            try:
                lang_button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'dropdown-toggle')]")
                lang_button.click()
                time.sleep(2)
                
                chinese_link = self.driver.find_element(By.XPATH, "//a[contains(text(), '简体中文')]")
                chinese_link.click()
                time.sleep(3)
                print("  ✓ 已切换到简体中文")
            except Exception as e:
                print(f"  ⚠ 语言切换失败（可能已是中文）: {str(e)}")
            
            # 登录页截图
            self.save_screenshot("系统登录", "登录页面（简体中文）", "票务系统登录界面")
            
            username_input = self.driver.find_element(By.NAME, "LoginInput.UserNameOrEmailAddress")
            password_input = self.driver.find_element(By.NAME, "LoginInput.Password")
            
            username_input.clear()
            username_input.send_keys(self.username)
            password_input.clear()
            password_input.send_keys(self.password)
            password_input.send_keys(Keys.RETURN)
            
            print("  ✓ 已提交登录")
            
            # 等待登录完成
            for i in range(15):
                time.sleep(1)
                current_url = self.driver.current_url
                if 'login' not in current_url.lower():
                    print(f"  ✓ 登录成功！")
                    break
            
            time.sleep(3)
            self.save_screenshot("系统主页", "主页Dashboard", "登录后主页")
            
            return True
        except Exception as e:
            print(f"✗ 登录失败: {str(e)}")
            return False
    
    def save_screenshot(self, module, function, description):
        """保存截图"""
        try:
            state_hash = self.get_page_state_hash()
            if state_hash and state_hash in self.visited_states:
                return False
            
            if state_hash:
                self.visited_states.add(state_hash)
            
            time.sleep(1.5)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.8)
            
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
                "url": self.driver.current_url,
                "title": self.driver.title
            })
            
            print(f"  [{self.screenshot_index:04d}] ✓ {module} - {function}")
            self.screenshot_index += 1
            return True
        except Exception as e:
            print(f"  ✗ 截图失败: {str(e)}")
            return False
    
    def click_element_safe(self, element):
        """安全点击元素"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
            try:
                element.click()
                return True
            except:
                self.driver.execute_script("arguments[0].click();", element)
                return True
        except:
            return False
    
    def get_first_level_menus(self):
        """获取一级菜单"""
        menus = []
        try:
            time.sleep(2)
            
            # 查找侧边栏的一级菜单
            links = self.driver.find_elements(By.XPATH, 
                "//aside//a[not(ancestor::ul[contains(@class, 'submenu')])] | " +
                "//nav//a[not(ancestor::ul[contains(@class, 'submenu')])]")
            
            for link in links:
                try:
                    if link.is_displayed():
                        text = link.text.strip()
                        if text and len(text) < 100 and text not in ['EN', 'CN', 'ZH']:
                            menus.append({
                                'text': text,
                                'element': link
                            })
                except:
                    pass
            
            # 去重
            seen = set()
            unique = []
            for item in menus:
                if item['text'] not in seen:
                    seen.add(item['text'])
                    unique.append(item)
            
            return unique
        except:
            return []
    
    def get_submenu_items(self):
        """获取当前展开的子菜单项"""
        submenus = []
        try:
            time.sleep(1.5)
            
            # 使用JavaScript强制展开所有子菜单
            self.driver.execute_script("""
                var innerMenus = document.querySelectorAll('.lpx-inner-menu');
                innerMenus.forEach(function(menu) {
                    menu.classList.remove('collapsed');
                    menu.style.display = 'block';
                });
            """)
            time.sleep(1)
            
            # 查找 lpx-inner-menu 中的链接
            sub_links = self.driver.find_elements(By.XPATH, 
                "//ul[contains(@class, 'lpx-inner-menu')]//a")
            
            print(f"      调试: 找到 {len(sub_links)} 个子菜单链接")
            
            for link in sub_links:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')
                    if text and len(text) < 100 and text not in ['', 'EN', 'CN', 'ZH']:
                        submenus.append({
                            'text': text,
                            'href': href,
                            'element': link
                        })
                except:
                    pass
            
            # 去重
            seen = set()
            unique = []
            for item in submenus:
                key = f"{item['text']}_{item.get('href', '')}"
                if key not in seen:
                    seen.add(key)
                    unique.append(item)
            
            return unique
        except Exception as e:
            print(f"      调试: 获取子菜单出错: {str(e)}")
            return []
    
    def find_page_buttons(self):
        """查找页面重要按钮"""
        buttons = []
        try:
            button_elements = self.driver.find_elements(By.XPATH, 
                "//button | //a[contains(@class, 'btn')] | //input[@type='submit'] | //input[@type='button']")
            
            important_keywords = ['新增', '新建', 'Add', 'Create', 'New', '添加', '编辑', 'Edit', 
                                 '查看', 'View', 'Details', '详情', '删除', 'Delete', 
                                 '设置', 'Setting', 'Config', '导出', 'Export', '导入', 'Import',
                                 '审核', 'Approve', '发布', 'Publish', '提交', 'Submit',
                                 '保存', 'Save', '取消', 'Cancel', '确定', 'OK', '搜索', 'Search']
            
            for btn in button_elements:
                try:
                    if btn.is_displayed() and btn.is_enabled():
                        text = btn.text.strip()
                        if text and len(text) < 50:
                            # 检查是否包含重要关键词
                            text_lower = text.lower()
                            if any(keyword.lower() in text_lower for keyword in important_keywords):
                                buttons.append({
                                    'element': btn,
                                    'text': text
                                })
                except:
                    pass
            
            # 去重
            seen = set()
            unique = []
            for btn in buttons:
                if btn['text'] not in seen:
                    seen.add(btn['text'])
                    unique.append(btn)
            
            return unique
        except:
            return []
    
    def explore_page_functions(self, module_name, page_name):
        """探索页面功能"""
        print(f"    → 探索页面功能...")
        
        buttons = self.find_page_buttons()
        print(f"      发现重要按钮: {len(buttons)} 个")
        
        for i, btn_info in enumerate(buttons[:8], 1):  # 限制8个
            try:
                btn_text = btn_info['text']
                print(f"        [{i}] 点击: {btn_text}")
                
                time.sleep(1)
                
                # 重新查找按钮
                fresh_buttons = self.find_page_buttons()
                target = None
                for fb in fresh_buttons:
                    if fb['text'] == btn_text:
                        target = fb['element']
                        break
                
                if target and self.click_element_safe(target):
                    time.sleep(2.5)
                    
                    function_name = f"{page_name} - {btn_text}"
                    self.save_screenshot(module_name, function_name, f"{btn_text}功能")
                    
                    # 尝试关闭弹窗或返回
                    try:
                        # 查找关闭按钮
                        close_btns = self.driver.find_elements(By.XPATH, 
                            "//button[contains(@class, 'close')] | " +
                            "//button[contains(text(), '取消')] | " +
                            "//button[contains(text(), 'Cancel')] | " +
                            "//button[contains(text(), '关闭')] | " +
                            "//a[contains(text(), '返回')]")
                        
                        for close_btn in close_btns:
                            if close_btn.is_displayed():
                                close_btn.click()
                                time.sleep(1)
                                break
                        else:
                            # 如果没有关闭按钮，尝试按ESC键
                            from selenium.webdriver.common.keys import Keys
                            from selenium.webdriver.common.action_chains import ActionChains
                            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                            time.sleep(1)
                    except:
                        pass
                    
                    time.sleep(1)
            except Exception as e:
                print(f"        ✗ 处理按钮出错: {str(e)}")
    
    def explore_all_menus(self):
        """遍历所有菜单（一级和二级）"""
        print("\n" + "=" * 80)
        print("开始全面遍历票务系统（包含子菜单）...")
        print("=" * 80)
        
        first_level_menus = self.get_first_level_menus()
        print(f"\n✓ 发现 {len(first_level_menus)} 个一级菜单\n")
        
        for i, menu1 in enumerate(first_level_menus, 1):
            try:
                print(f"\n{'='*80}")
                print(f"[{i}/{len(first_level_menus)}] 一级菜单: {menu1['text']}")
                print(f"{'='*80}")
                
                # 返回主页并重新查找菜单
                self.driver.get(self.base_url)
                time.sleep(2)
                
                fresh_menus = self.get_first_level_menus()
                target_menu = None
                for fm in fresh_menus:
                    if fm['text'] == menu1['text']:
                        target_menu = fm['element']
                        break
                
                if not target_menu:
                    print(f"  ✗ 未找到菜单: {menu1['text']}")
                    continue
                
                # 点击一级菜单
                if self.click_element_safe(target_menu):
                    time.sleep(2)
                    
                    # 获取子菜单
                    submenus = self.get_submenu_items()
                    
                    if submenus:
                        print(f"  → 发现 {len(submenus)} 个子菜单")
                        
                        # 遍历子菜单
                        for j, submenu in enumerate(submenus, 1):
                            try:
                                print(f"\n  [{i}.{j}] 子菜单: {submenu['text']}")
                                
                                # 返回主页并重新导航
                                self.driver.get(self.base_url)
                                time.sleep(2)
                                
                                # 重新点击一级菜单
                                fresh_menus = self.get_first_level_menus()
                                target_menu = None
                                for fm in fresh_menus:
                                    if fm['text'] == menu1['text']:
                                        target_menu = fm['element']
                                        break
                                
                                if target_menu:
                                    self.click_element_safe(target_menu)
                                    time.sleep(2)
                                
                                # 重新查找并点击子菜单
                                fresh_submenus = self.get_submenu_items()
                                target_submenu = None
                                for fs in fresh_submenus:
                                    if fs['text'] == submenu['text']:
                                        target_submenu = fs['element']
                                        break
                                
                                if target_submenu and self.click_element_safe(target_submenu):
                                    time.sleep(3)
                                    
                                    # 截图子菜单页面
                                    self.save_screenshot(
                                        f"{menu1['text']}",
                                        f"{submenu['text']}",
                                        f"{menu1['text']} - {submenu['text']}"
                                    )
                                    
                                    # 探索页面功能
                                    self.explore_page_functions(menu1['text'], submenu['text'])
                                
                            except Exception as e:
                                print(f"  ✗ 处理子菜单出错: {str(e)}")
                    else:
                        # 没有子菜单，直接截图
                        print(f"  → 无子菜单，直接截图")
                        self.save_screenshot(menu1['text'], f"{menu1['text']}页面", f"{menu1['text']}功能模块")
                        self.explore_page_functions(menu1['text'], menu1['text'])
                
                print()
                
            except Exception as e:
                print(f"✗ 处理一级菜单出错: {str(e)}\n")
        
        print("=" * 80)
        print(f"✓ 遍历完成！共截图 {len(self.screenshots)} 个功能点")
        print("=" * 80)
    
    def close(self):
        if self.driver:
            self.driver.quit()


def create_word_document(screenshots, output_path):
    """生成Word文档"""
    print("\n正在生成Word文档...")
    
    doc = Document()
    doc.styles['Normal'].font.name = 'Microsoft YaHei'
    doc.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    
    title = doc.add_heading('票务系统 - 完整功能截图文档', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    info = doc.add_paragraph()
    info.add_run('系统名称：').bold = True
    info.add_run('票务系统（亿思维智慧门店）\n')
    info.add_run('系统地址：').bold = True
    info.add_run('https://xstest.axioxio.com/\n')
    info.add_run('生成时间：').bold = True
    info.add_run(f'{time.strftime("%Y-%m-%d %H:%M:%S")}\n')
    info.add_run('截图总数：').bold = True
    info.add_run(f'{len(screenshots)} 张')
    
    doc.add_paragraph()
    
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    
    header = table.rows[0].cells
    header[0].text = '序号'
    header[1].text = '功能模块 / 功能点'
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
        run.font.color.rgb = None
        
        img_path = os.path.join('/workspace/screenshots_ticket_complete', ss['filename'])
        if os.path.exists(img_path):
            img_para = cells[2].paragraphs[0]
            img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            try:
                run = img_para.add_run()
                run.add_picture(img_path, width=Inches(3.8))
            except:
                img_para.add_run('[图片加载失败]')
    
    doc.save(output_path)
    print(f"✓ Word文档: {output_path} ({os.path.getsize(output_path) / 1024 / 1024:.2f} MB)")


def main():
    base_url = "https://xstest.axioxio.com/"
    username = "13811458301"
    password = "4<z%0/RS"
    
    print("=" * 80)
    print("票务系统完整截图工具（包含子菜单）")
    print("=" * 80)
    
    screenshotter = None
    try:
        screenshotter = TicketSystemCompleteScreenshotter(base_url, username, password)
        
        if screenshotter.login():
            screenshotter.explore_all_menus()
            
            # 保存JSON
            json_path = os.path.join('screenshots_ticket_complete', 'index.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'total': len(screenshotter.screenshots),
                    'screenshots': screenshotter.screenshots
                }, f, ensure_ascii=False, indent=2)
            
            # 生成Word
            doc_path = '/workspace/票务系统完整功能截图文档.docx'
            create_word_document(screenshotter.screenshots, doc_path)
            
            # 打包
            print("\n正在打包...")
            os.system("cd /workspace && rm -f 票务系统完整功能截图包.zip && zip -q -r 票务系统完整功能截图包.zip screenshots_ticket_complete/ 票务系统完整功能截图文档.docx")
            
            print("\n" + "=" * 80)
            print("✅ 完成！")
            print(f"📊 截图总数: {len(screenshotter.screenshots)} 张")
            print(f"📄 Word文档: {doc_path}")
            print(f"📦 压缩包: /workspace/票务系统完整功能截图包.zip")
            print("=" * 80)
        else:
            print("\n❌ 登录失败")
    
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if screenshotter:
            screenshotter.close()
            print("\n浏览器已关闭")


if __name__ == "__main__":
    main()
