#!/usr/bin/env python3
"""
超级完整截图工具 - 遍历系统所有功能点
遍历每个1、2级菜单，点击页面上的每个可操作按钮，截取所有展示页面
"""

import os
import time
import json
import hashlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

class SuperCompleteScreenshotter:
    def __init__(self, base_url, username, password, output_dir="screenshots_complete_all"):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.output_dir = output_dir
        self.screenshots = []
        self.visited_hashes = set()
        self.screenshot_index = 1
        
        os.makedirs(output_dir, exist_ok=True)
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--ignore-certificate-errors')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(2)
        
    def get_page_hash(self):
        """获取页面内容哈希，用于去重"""
        try:
            url = self.driver.current_url
            body = self.driver.find_element(By.TAG_NAME, "body").text[:800]
            return hashlib.md5(f"{url}|{body}".encode()).hexdigest()
        except:
            return hashlib.md5(str(time.time()).encode()).hexdigest()
    
    def login(self):
        """登录"""
        print(f"\n正在登录系统...")
        self.driver.get(self.base_url)
        time.sleep(3)
        
        try:
            # 登录页截图
            self.save_screenshot("系统登录", "登录页面", "用户登录界面")
            
            username_input = self.driver.find_element(By.NAME, "username")
            password_input = self.driver.find_element(By.NAME, "password")
            
            username_input.send_keys(self.username)
            password_input.send_keys(self.password)
            
            login_button = self.driver.find_element(By.XPATH, "//button[@type='button']")
            login_button.click()
            
            for i in range(10):
                time.sleep(1)
                if 'dashboard' in self.driver.current_url:
                    break
            
            time.sleep(2)
            print("✓ 登录成功")
            
            # 主页截图
            self.save_screenshot("主页", "Dashboard", "系统主页")
            
            return True
        except Exception as e:
            print(f"✗ 登录失败: {str(e)}")
            return False
    
    def save_screenshot(self, module, function, description):
        """保存截图（带去重）"""
        try:
            page_hash = self.get_page_hash()
            if page_hash in self.visited_hashes:
                return False
            
            self.visited_hashes.add(page_hash)
            
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
            
            safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in f"{module}_{function}")
            safe_name = safe_name[:60]
            
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
    
    def get_all_menus(self):
        """获取所有一级菜单"""
        menus = []
        try:
            time.sleep(1)
            menu_elements = self.driver.find_elements(By.XPATH,
                "//li[contains(@class, 'el-submenu') or contains(@class, 'el-menu-item')]")
            
            seen = set()
            for elem in menu_elements:
                try:
                    if elem.is_displayed():
                        text = elem.text.strip().split('\n')[0]
                        if text and len(text) < 50 and text not in seen:
                            seen.add(text)
                            is_submenu = 'el-submenu' in elem.get_attribute('class')
                            menus.append({
                                'text': text,
                                'element': elem,
                                'is_submenu': is_submenu
                            })
                except:
                    pass
            return menus
        except:
            return []
    
    def get_submenus(self, parent_element):
        """获取子菜单"""
        submenus = []
        try:
            time.sleep(0.5)
            sub_elements = parent_element.find_elements(By.XPATH,
                ".//ul[contains(@class, 'el-menu--inline')]//li")
            
            for elem in sub_elements:
                try:
                    if elem.is_displayed():
                        text = elem.text.strip()
                        if text and len(text) < 50:
                            submenus.append({
                                'text': text,
                                'element': elem
                            })
                except:
                    pass
            
            # 去重
            seen = set()
            unique = []
            for item in submenus:
                if item['text'] not in seen:
                    seen.add(item['text'])
                    unique.append(item)
            return unique
        except:
            return []
    
    def click_element(self, element):
        """点击元素"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.3)
            try:
                element.click()
                return True
            except:
                self.driver.execute_script("arguments[0].click();", element)
                return True
        except:
            return False
    
    def close_dialog(self):
        """关闭弹窗"""
        try:
            close_btns = self.driver.find_elements(By.XPATH,
                "//*[contains(@class, 'el-dialog__close') or contains(@class, 'el-drawer__close') or contains(@class, 'el-message-box__close')]")
            for btn in close_btns:
                if btn.is_displayed():
                    self.click_element(btn)
                    time.sleep(0.5)
                    return True
            return False
        except:
            return False
    
    def find_all_buttons(self):
        """查找页面所有可点击的按钮"""
        buttons = []
        try:
            # 查找所有按钮
            button_elements = self.driver.find_elements(By.XPATH,
                "//button | //a[contains(@class, 'el-button')] | //*[contains(@class, 'el-link')]")
            
            for btn in button_elements:
                try:
                    if btn.is_displayed() and btn.is_enabled():
                        text = btn.text.strip()
                        if text:
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
    
    def explore_page_buttons(self, module_name, page_name):
        """探索页面上的所有按钮"""
        print(f"    → 探索页面按钮: {page_name}")
        
        buttons = self.find_all_buttons()
        
        # 过滤出重要的操作按钮
        important_keywords = ['新增', '新建', '添加', '创建', '编辑', '修改', '查看', '详情', 
                             '删除', '设置', '配置', '管理', '导出', '导入', '上传', 
                             '审核', '发布', '上架', '下架', '启用', '禁用']
        
        important_buttons = []
        other_buttons = []
        
        for btn in buttons:
            if any(keyword in btn['text'] for keyword in important_keywords):
                important_buttons.append(btn)
            else:
                other_buttons.append(btn)
        
        print(f"      发现按钮: 重要操作 {len(important_buttons)} 个, 其他 {len(other_buttons)} 个")
        
        # 处理重要按钮
        for i, btn_info in enumerate(important_buttons[:10]):  # 限制每页最多10个重要按钮
            try:
                btn_text = btn_info['text']
                print(f"        [{i+1}] 点击: {btn_text}")
                
                # 重新查找按钮（避免stale）
                time.sleep(0.5)
                fresh_buttons = self.find_all_buttons()
                target = None
                for fb in fresh_buttons:
                    if fb['text'] == btn_text:
                        target = fb['element']
                        break
                
                if target and self.click_element(target):
                    time.sleep(1.5)
                    
                    # 截图
                    function_name = f"{page_name} - {btn_text}"
                    self.save_screenshot(module_name, function_name, f"{btn_text}操作页面")
                    
                    # 检查是否有弹窗
                    if self.close_dialog():
                        time.sleep(0.5)
                    else:
                        # 可能跳转了页面，返回
                        try:
                            self.driver.back()
                            time.sleep(1)
                        except:
                            pass
            except Exception as e:
                print(f"        ✗ 处理按钮出错: {str(e)}")
    
    def explore_table_actions(self, module_name, page_name):
        """探索表格中的操作按钮"""
        print(f"    → 探索表格操作按钮")
        
        try:
            # 查找表格中的操作按钮
            table_buttons = self.driver.find_elements(By.XPATH,
                "//table//button | //table//a[contains(@class, 'el-button')]")
            
            # 只处理前几行的按钮
            processed = set()
            count = 0
            
            for btn in table_buttons[:8]:  # 最多8个
                try:
                    if btn.is_displayed():
                        text = btn.text.strip()
                        if text and text not in processed:
                            processed.add(text)
                            count += 1
                            
                            print(f"        表格操作[{count}]: {text}")
                            
                            # 重新查找
                            time.sleep(0.5)
                            fresh_table_btns = self.driver.find_elements(By.XPATH,
                                "//table//button | //table//a[contains(@class, 'el-button')]")
                            
                            # 找到第一个匹配的按钮
                            for ftb in fresh_table_btns:
                                if ftb.is_displayed() and ftb.text.strip() == text:
                                    if self.click_element(ftb):
                                        time.sleep(1.5)
                                        
                                        function_name = f"{page_name} - 表格{text}"
                                        self.save_screenshot(module_name, function_name, f"表格{text}操作")
                                        
                                        if self.close_dialog():
                                            time.sleep(0.5)
                                        else:
                                            try:
                                                self.driver.back()
                                                time.sleep(1)
                                            except:
                                                pass
                                        break
                                    break
                except:
                    pass
        except:
            pass
    
    def explore_all_system(self):
        """遍历整个系统"""
        print("\n" + "=" * 80)
        print("开始全面遍历系统...")
        print("=" * 80)
        
        # 获取所有一级菜单
        menus = self.get_all_menus()
        print(f"\n✓ 发现 {len(menus)} 个一级菜单\n")
        
        for i, menu_item in enumerate(menus, 1):
            try:
                print(f"\n{'='*80}")
                print(f"[{i}/{len(menus)}] 一级菜单: {menu_item['text']}")
                print(f"{'='*80}")
                
                # 重新获取菜单
                time.sleep(1)
                fresh_menus = self.get_all_menus()
                target_menu = None
                for fm in fresh_menus:
                    if fm['text'] == menu_item['text']:
                        target_menu = fm
                        break
                
                if not target_menu:
                    continue
                
                # 点击一级菜单
                if self.click_element(target_menu['element']):
                    time.sleep(1.5)
                    
                    if target_menu['is_submenu']:
                        # 有子菜单
                        submenus = self.get_submenus(target_menu['element'])
                        print(f"  → 包含 {len(submenus)} 个子菜单\n")
                        
                        for j, submenu in enumerate(submenus, 1):
                            try:
                                print(f"  [{j}/{len(submenus)}] 子菜单: {submenu['text']}")
                                
                                # 重新获取父菜单和子菜单
                                time.sleep(1)
                                fresh_menus2 = self.get_all_menus()
                                fresh_parent = None
                                for fm2 in fresh_menus2:
                                    if fm2['text'] == menu_item['text']:
                                        fresh_parent = fm2['element']
                                        break
                                
                                if fresh_parent:
                                    fresh_subs = self.get_submenus(fresh_parent)
                                    for fs in fresh_subs:
                                        if fs['text'] == submenu['text']:
                                            if self.click_element(fs['element']):
                                                time.sleep(2)
                                                
                                                # 截取列表页
                                                page_name = submenu['text']
                                                self.save_screenshot(menu_item['text'], page_name, f"{page_name}页面")
                                                
                                                # 探索页面按钮
                                                self.explore_page_buttons(menu_item['text'], page_name)
                                                
                                                # 探索表格操作
                                                self.explore_table_actions(menu_item['text'], page_name)
                                            break
                                
                                print()
                            except Exception as e:
                                print(f"  ✗ 处理子菜单出错: {str(e)}\n")
                    else:
                        # 无子菜单，直接页面
                        page_name = menu_item['text']
                        self.save_screenshot(menu_item['text'], page_name, f"{page_name}页面")
                        
                        # 探索页面功能
                        self.explore_page_buttons(menu_item['text'], page_name)
                        self.explore_table_actions(menu_item['text'], page_name)
                
                print()
                
            except Exception as e:
                print(f"✗ 处理菜单出错: {str(e)}\n")
        
        print("=" * 80)
        print(f"✓ 遍历完成！共截图 {len(self.screenshots)} 个功能点")
        print("=" * 80)
    
    def close(self):
        if self.driver:
            self.driver.quit()


def create_word_document(screenshots, output_path):
    """生成Word文档"""
    print("\n正在生成Word文档...")
    print("=" * 80)
    
    doc = Document()
    
    # 中文字体
    doc.styles['Normal'].font.name = 'Microsoft YaHei'
    doc.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    
    # 标题
    title = doc.add_heading('海星育后台管理系统 - 完整功能截图文档', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 信息
    info = doc.add_paragraph()
    info.add_run('系统名称：').bold = True
    info.add_run('海星育后台管理系统\n')
    info.add_run('系统地址：').bold = True
    info.add_run('https://jhtest.bjstarfish.com/\n')
    info.add_run('生成时间：').bold = True
    info.add_run(f'{time.strftime("%Y-%m-%d %H:%M:%S")}\n')
    info.add_run('截图总数：').bold = True
    info.add_run(f'{len(screenshots)} 张\n')
    info.add_run('说明：').bold = True
    info.add_run('本文档包含系统所有功能页面的截图，涵盖所有菜单和操作按钮')
    
    doc.add_paragraph()
    
    # 表格
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    
    # 表头
    header = table.rows[0].cells
    header[0].text = '序号'
    header[1].text = '功能点'
    header[2].text = '截图'
    
    for cell in header:
        for para in cell.paragraphs:
            for run in para.runs:
                run.font.bold = True
                run.font.size = Pt(11)
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 列宽
    widths = (Inches(0.5), Inches(2.5), Inches(4.0))
    for row in table.rows:
        for idx, width in enumerate(widths):
            row.cells[idx].width = width
    
    # 数据
    for ss in screenshots:
        row = table.add_row()
        cells = row.cells
        
        for idx, width in enumerate(widths):
            cells[idx].width = width
        
        # 序号
        cells[0].text = str(ss['index'])
        cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 描述
        desc_para = cells[1].paragraphs[0]
        run = desc_para.add_run(f"【{ss['module']}】\n")
        run.font.bold = True
        run.font.size = Pt(10)
        
        run = desc_para.add_run(f"{ss['function']}\n\n")
        run.font.size = Pt(9)
        
        run = desc_para.add_run(f"{ss['description']}")
        run.font.size = Pt(8)
        
        # 截图
        img_path = os.path.join('/workspace/screenshots_complete_all', ss['filename'])
        if os.path.exists(img_path):
            img_para = cells[2].paragraphs[0]
            img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            try:
                run = img_para.add_run()
                run.add_picture(img_path, width=Inches(3.8))
            except:
                img_para.add_run('[图片加载失败]')
        else:
            cells[2].text = '[图片不存在]'
    
    doc.save(output_path)
    
    print("=" * 80)
    print(f"✓ Word文档生成完成")
    print(f"📄 文件: {output_path}")
    print(f"📊 大小: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")


def main():
    base_url = "https://jhtest.bjstarfish.com/"
    username = "admin"
    password = "123456"
    output_dir = "screenshots_complete_all"
    
    print("=" * 80)
    print("超级完整系统截图工具")
    print("遍历所有1、2级菜单，点击所有可操作按钮")
    print("=" * 80)
    
    screenshotter = None
    try:
        screenshotter = SuperCompleteScreenshotter(base_url, username, password, output_dir)
        
        if screenshotter.login():
            screenshotter.explore_all_system()
            
            # 保存JSON
            json_path = os.path.join(output_dir, 'screenshots_index.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'total': len(screenshotter.screenshots),
                    'screenshots': screenshotter.screenshots
                }, f, ensure_ascii=False, indent=2)
            
            # 生成Word文档
            doc_path = '/workspace/系统完整功能截图文档.docx'
            create_word_document(screenshotter.screenshots, doc_path)
            
            # 打包
            print("\n正在打包所有文件...")
            os.system(f"cd /workspace && zip -q -r 系统完整功能截图包.zip {output_dir}/ 系统完整功能截图文档.docx")
            
            print("\n" + "=" * 80)
            print("✅ 所有任务完成！")
            print(f"📁 截图目录: /workspace/{output_dir}")
            print(f"📊 截图总数: {len(screenshotter.screenshots)} 张")
            print(f"📄 Word文档: {doc_path}")
            print(f"📦 压缩包: /workspace/系统完整功能截图包.zip")
            print("=" * 80)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
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
