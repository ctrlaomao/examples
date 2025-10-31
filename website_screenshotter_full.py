#!/usr/bin/env python3
"""
终极完整版自动化网站截图工具
- 遍历所有菜单（包括子菜单）
- 点击所有操作按钮（新增、编辑、查看详情等）
- 截取所有弹窗和对话框
- 尽可能覆盖系统的所有页面
"""

import os
import time
import hashlib
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains


class FullSystemScreenshotter:
    def __init__(self, base_url, username, password, output_dir="screenshots_full"):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.output_dir = output_dir
        self.visited_views = set()
        self.screenshots = []
        self.screenshot_index = 1
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 配置 Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--ignore-certificate-errors')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(3)
        
    def get_page_hash(self):
        """获取当前页面的哈希值"""
        try:
            url_hash = self.driver.current_url
            # 获取页面主要内容
            try:
                main_content = self.driver.find_element(By.TAG_NAME, "body").text[:500]
            except:
                main_content = ""
            
            return hashlib.md5(f"{url_hash}|{main_content}".encode()).hexdigest()
        except:
            return hashlib.md5(str(time.time()).encode()).hexdigest()
    
    def login(self):
        """登录网站"""
        print(f"\n正在访问登录页面: {self.base_url}")
        self.driver.get(self.base_url)
        time.sleep(3)
        
        try:
            login_ss = os.path.join(self.output_dir, "00_login_page.png")
            self.driver.save_screenshot(login_ss)
            print(f"✓ 已保存登录页截图")
            
            username_input = self.driver.find_element(By.NAME, "username")
            password_input = self.driver.find_element(By.NAME, "password")
            
            username_input.clear()
            username_input.send_keys(self.username)
            password_input.clear()
            password_input.send_keys(self.password)
            
            login_button = self.driver.find_element(By.XPATH, "//button[@type='button']")
            login_button.click()
            print("✓ 已点击登录按钮")
            
            # 等待登录完成
            for i in range(10):
                time.sleep(1)
                if 'dashboard' in self.driver.current_url:
                    break
            
            time.sleep(3)
            
            after_login_ss = os.path.join(self.output_dir, "01_after_login.png")
            self.driver.save_screenshot(after_login_ss)
            print(f"✓ 登录成功！")
            
            return True
            
        except Exception as e:
            print(f"✗ 登录失败: {str(e)}")
            return False
    
    def take_screenshot(self, name, force=False):
        """截取当前页面"""
        try:
            page_hash = self.get_page_hash()
            if not force and page_hash in self.visited_views:
                return False
            
            self.visited_views.add(page_hash)
            
            time.sleep(1.5)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
            
            safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_', '(', ')') else '_' for c in name)
            safe_name = safe_name.strip().replace(' ', '_')[:80]
            
            filename = f"{self.screenshot_index:03d}_{safe_name}_{page_hash[:8]}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            self.driver.save_screenshot(filepath)
            
            self.screenshots.append({
                "index": self.screenshot_index,
                "name": name,
                "url": self.driver.current_url,
                "title": self.driver.title,
                "filename": filename
            })
            
            print(f"  [{self.screenshot_index:03d}] ✓ {name}")
            self.screenshot_index += 1
            
            return True
            
        except Exception as e:
            print(f"  ✗ 截图失败: {str(e)}")
            return False
    
    def click_element(self, element):
        """尝试多种方式点击元素"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.3)
            
            try:
                element.click()
                return True
            except:
                pass
            
            try:
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except:
                pass
            
            try:
                ActionChains(self.driver).move_to_element(element).click().perform()
                return True
            except:
                pass
            
            return False
        except:
            return False
    
    def find_action_buttons(self):
        """查找页面上的所有操作按钮"""
        buttons = []
        
        # 常见的操作按钮文本
        button_texts = [
            '新增', '添加', '新建', '创建',
            '编辑', '修改', '查看', '详情',
            '设置', '配置', '管理',
            '搜索', '查询', '筛选'
        ]
        
        try:
            # 查找所有按钮
            all_buttons = self.driver.find_elements(By.XPATH, 
                "//button | //a[contains(@class, 'el-button')] | //*[contains(@class, 'btn')]")
            
            for btn in all_buttons:
                try:
                    if btn.is_displayed() and btn.is_enabled():
                        text = btn.text.strip()
                        # 检查是否包含关键词
                        if any(keyword in text for keyword in button_texts):
                            buttons.append({
                                'element': btn,
                                'text': text
                            })
                except:
                    pass
            
            return buttons
        except:
            return []
    
    def find_table_action_buttons(self):
        """查找表格中的操作按钮（如编辑、查看详情）"""
        buttons = []
        
        try:
            # 查找表格中的操作列
            action_buttons = self.driver.find_elements(By.XPATH,
                "//table//button | //table//a[contains(@class, 'el-button')]")
            
            # 只取前几行的操作按钮（避免太多重复）
            for btn in action_buttons[:6]:  # 只处理前6个
                try:
                    if btn.is_displayed():
                        text = btn.text.strip()
                        if text:
                            buttons.append({
                                'element': btn,
                                'text': text
                            })
                except:
                    pass
            
            return buttons
        except:
            return []
    
    def handle_dialog_or_drawer(self, context_name):
        """处理弹窗或抽屉"""
        try:
            time.sleep(1)
            
            # 检查是否有弹窗或抽屉
            dialogs = self.driver.find_elements(By.XPATH,
                "//*[contains(@class, 'el-dialog') or contains(@class, 'el-drawer')]")
            
            for dialog in dialogs:
                try:
                    if dialog.is_displayed():
                        # 截取弹窗
                        self.take_screenshot(f"{context_name} - 弹窗", force=True)
                        
                        # 尝试关闭弹窗
                        close_buttons = dialog.find_elements(By.XPATH,
                            ".//*[contains(@class, 'el-dialog__close') or contains(@class, 'el-drawer__close')]")
                        
                        for close_btn in close_buttons:
                            if close_btn.is_displayed():
                                self.click_element(close_btn)
                                time.sleep(0.5)
                                break
                        
                        return True
                except:
                    pass
            
            return False
        except:
            return False
    
    def explore_page_actions(self, page_name):
        """探索当前页面的所有操作"""
        print(f"    → 探索页面操作: {page_name}")
        
        # 1. 查找并点击顶部操作按钮（新增、添加等）
        action_buttons = self.find_action_buttons()
        
        if action_buttons:
            print(f"    → 发现 {len(action_buttons)} 个操作按钮")
            
            for i, btn_info in enumerate(action_buttons[:5]):  # 限制处理前5个
                try:
                    btn_text = btn_info['text']
                    print(f"      [{i+1}] 点击按钮: {btn_text}")
                    
                    # 重新查找按钮（避免stale）
                    time.sleep(0.5)
                    fresh_buttons = self.find_action_buttons()
                    target_btn = None
                    
                    for fb in fresh_buttons:
                        if fb['text'] == btn_text:
                            target_btn = fb['element']
                            break
                    
                    if target_btn and self.click_element(target_btn):
                        time.sleep(1.5)
                        
                        # 检查是否有弹窗
                        if self.handle_dialog_or_drawer(f"{page_name} - {btn_text}"):
                            print(f"      ✓ 已截取弹窗")
                        else:
                            # 可能跳转到了新页面
                            self.take_screenshot(f"{page_name} - {btn_text}")
                            # 返回上一页
                            self.driver.back()
                            time.sleep(1)
                
                except Exception as e:
                    print(f"      ✗ 处理按钮出错: {str(e)}")
        
        # 2. 查找并点击表格中的操作按钮（查看详情、编辑等）
        table_buttons = self.find_table_action_buttons()
        
        if table_buttons:
            print(f"    → 发现表格操作按钮 {len(table_buttons)} 个")
            
            for i, btn_info in enumerate(table_buttons[:3]):  # 只处理前3个
                try:
                    btn_text = btn_info['text']
                    print(f"      [{i+1}] 点击表格按钮: {btn_text}")
                    
                    time.sleep(0.5)
                    fresh_table_buttons = self.find_table_action_buttons()
                    
                    if i < len(fresh_table_buttons):
                        target_btn = fresh_table_buttons[i]['element']
                        
                        if self.click_element(target_btn):
                            time.sleep(1.5)
                            
                            # 检查弹窗或新页面
                            if self.handle_dialog_or_drawer(f"{page_name} - {btn_text}"):
                                print(f"      ✓ 已截取弹窗")
                            else:
                                self.take_screenshot(f"{page_name} - {btn_text}")
                                self.driver.back()
                                time.sleep(1)
                
                except Exception as e:
                    print(f"      ✗ 处理表格按钮出错: {str(e)}")
    
    def get_all_menu_items(self):
        """获取所有菜单项"""
        menu_items = []
        try:
            time.sleep(1)
            
            all_menus = self.driver.find_elements(By.XPATH,
                "//li[contains(@class, 'el-submenu')] | //li[contains(@class, 'el-menu-item')]")
            
            seen = set()
            for elem in all_menus:
                try:
                    if elem.is_displayed():
                        text = elem.text.strip().split('\n')[0]
                        if text and len(text) < 50 and text not in seen:
                            seen.add(text)
                            is_submenu = 'el-submenu' in elem.get_attribute('class')
                            menu_items.append({
                                'text': text,
                                'element': elem,
                                'is_submenu': is_submenu
                            })
                except:
                    pass
            
            return menu_items
        except:
            return []
    
    def get_submenu_items(self, parent_element):
        """获取子菜单项"""
        submenu_items = []
        try:
            time.sleep(0.5)
            sub_elements = parent_element.find_elements(By.XPATH,
                ".//ul[contains(@class, 'el-menu--inline')]//li")
            
            for sub_elem in sub_elements:
                try:
                    if sub_elem.is_displayed():
                        text = sub_elem.text.strip()
                        if text and len(text) < 50:
                            submenu_items.append({
                                'text': text,
                                'element': sub_elem
                            })
                except:
                    pass
            
            # 去重
            seen = set()
            unique = []
            for item in submenu_items:
                if item['text'] not in seen:
                    seen.add(item['text'])
                    unique.append(item)
            
            return unique
        except:
            return []
    
    def explore_all_system(self):
        """遍历整个系统的所有页面"""
        print("\n开始全面遍历系统...")
        print("=" * 60)
        
        # 截取主页
        self.take_screenshot("主页_Dashboard")
        self.explore_page_actions("主页")
        
        # 获取所有菜单
        menu_items = self.get_all_menu_items()
        print(f"\n✓ 发现 {len(menu_items)} 个菜单项\n")
        
        # 遍历每个菜单
        for i, item in enumerate(menu_items):
            try:
                print(f"{'='*60}")
                print(f"[{i+1}/{len(menu_items)}] 正在处理菜单: {item['text']}")
                print(f"{'='*60}")
                
                time.sleep(1)
                fresh_menus = self.get_all_menu_items()
                
                target = None
                for fm in fresh_menus:
                    if fm['text'] == item['text']:
                        target = fm
                        break
                
                if not target:
                    continue
                
                if target['is_submenu']:
                    print(f"  → 包含子菜单")
                    
                    if self.click_element(target['element']):
                        time.sleep(1)
                        
                        submenus = self.get_submenu_items(target['element'])
                        
                        if submenus:
                            print(f"  → 发现 {len(submenus)} 个子菜单\n")
                            
                            for j, sub in enumerate(submenus):
                                try:
                                    print(f"  [{j+1}/{len(submenus)}] 子菜单: {sub['text']}")
                                    
                                    time.sleep(0.5)
                                    fresh_parent = None
                                    for fp in self.get_all_menu_items():
                                        if fp['text'] == item['text']:
                                            fresh_parent = fp['element']
                                            break
                                    
                                    if fresh_parent:
                                        fresh_subs = self.get_submenu_items(fresh_parent)
                                        for fs in fresh_subs:
                                            if fs['text'] == sub['text']:
                                                if self.click_element(fs['element']):
                                                    time.sleep(2)
                                                    page_name = f"{item['text']} - {sub['text']}"
                                                    self.take_screenshot(page_name)
                                                    
                                                    # 探索页面操作
                                                    self.explore_page_actions(page_name)
                                                break
                                    
                                    print()
                                
                                except Exception as e:
                                    print(f"  ✗ 处理子菜单出错: {str(e)}\n")
                        else:
                            time.sleep(1.5)
                            self.take_screenshot(item['text'])
                            self.explore_page_actions(item['text'])
                
                else:
                    # 普通菜单项
                    if self.click_element(target['element']):
                        time.sleep(2)
                        self.take_screenshot(item['text'])
                        
                        # 探索页面操作
                        self.explore_page_actions(item['text'])
                
                print()
                
            except Exception as e:
                print(f"✗ 处理菜单出错: {str(e)}\n")
        
        print("=" * 60)
        print(f"✓ 遍历完成！共截图 {len(self.screenshots)} 个页面")
        print("=" * 60)
    
    def save_report(self):
        """保存报告"""
        report_file = os.path.join(self.output_dir, "report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "base_url": self.base_url,
                "total_screenshots": len(self.screenshots),
                "screenshots": self.screenshots
            }, f, ensure_ascii=False, indent=2)
        
        html_file = os.path.join(self.output_dir, "report.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>完整系统截图报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Microsoft YaHei', 'Segoe UI', Tahoma, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #333;
            font-size: 36px;
            margin-bottom: 30px;
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }}
        .stat-number {{
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .stat-label {{
            font-size: 16px;
            opacity: 0.9;
        }}
        .screenshot-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }}
        .screenshot-card {{
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        .screenshot-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }}
        .screenshot-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
        }}
        .screenshot-number {{
            font-size: 14px;
            opacity: 0.8;
            margin-bottom: 5px;
        }}
        .screenshot-title {{
            font-size: 18px;
            font-weight: bold;
        }}
        .screenshot-img {{
            width: 100%;
            height: 300px;
            object-fit: cover;
            cursor: pointer;
            transition: transform 0.3s;
        }}
        .screenshot-img:hover {{
            transform: scale(1.05);
        }}
        .screenshot-meta {{
            padding: 15px;
            background: #f8f9fa;
            font-size: 12px;
            color: #666;
        }}
        .info-banner {{
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 完整系统截图报告</h1>
        
        <div class="info-banner">
            <p><strong>📍 网站:</strong> {self.base_url}</p>
            <p><strong>⏰ 生成时间:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(self.screenshots)}</div>
                <div class="stat-label">总截图数</div>
            </div>
        </div>
        
        <div class="screenshot-grid">
""")
            
            for screenshot in self.screenshots:
                f.write(f"""
            <div class="screenshot-card">
                <div class="screenshot-header">
                    <div class="screenshot-number">#{screenshot['index']:03d}</div>
                    <div class="screenshot-title">{screenshot['name']}</div>
                </div>
                <img src="{screenshot['filename']}" alt="{screenshot['name']}" 
                     class="screenshot-img" onclick="window.open(this.src)" 
                     title="点击查看大图">
                <div class="screenshot-meta">
                    <div><strong>标题:</strong> {screenshot['title']}</div>
                    <div><strong>URL:</strong> {screenshot['url'][:60]}...</div>
                </div>
            </div>
""")
            
            f.write("""
        </div>
    </div>
</body>
</html>
""")
        
        print(f"\n✓ 已保存 JSON 报告: {report_file}")
        print(f"✓ 已保存 HTML 报告: {html_file}")
    
    def close(self):
        if self.driver:
            self.driver.quit()


def main():
    base_url = "https://jhtest.bjstarfish.com/"
    username = "admin"
    password = "123456"
    output_dir = "screenshots_full"
    
    print("=" * 60)
    print("🚀 终极完整版自动化网站截图工具")
    print("=" * 60)
    print(f"📍 目标网站: {base_url}")
    print(f"👤 用户名: {username}")
    print(f"📁 输出目录: {output_dir}")
    print(f"🎯 功能: 遍历所有菜单 + 所有操作按钮 + 所有弹窗")
    print("=" * 60)
    
    screenshotter = None
    try:
        screenshotter = FullSystemScreenshotter(base_url, username, password, output_dir)
        
        if screenshotter.login():
            screenshotter.explore_all_system()
            screenshotter.save_report()
            
            print("\n" + "=" * 60)
            print("✅ 所有任务完成！")
            print(f"📁 截图保存位置: {os.path.abspath(output_dir)}")
            print(f"📊 总截图数: {len(screenshotter.screenshots)}")
            print(f"📄 查看报告: {os.path.join(output_dir, 'report.html')}")
            print("=" * 60)
        else:
            print("\n❌ 登录失败")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if screenshotter:
            screenshotter.close()
            print("\n浏览器已关闭")


if __name__ == "__main__":
    main()
