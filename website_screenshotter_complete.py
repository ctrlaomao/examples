#!/usr/bin/env python3
"""
完整版自动化网站截图工具 - 遍历所有菜单（包括子菜单）
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


class CompleteScreenshotter:
    def __init__(self, base_url, username, password, output_dir="screenshots"):
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
            title = self.driver.title
            return hashlib.md5(f"{url_hash}|{title}".encode()).hexdigest()
        except:
            return hashlib.md5(str(time.time()).encode()).hexdigest()
    
    def login(self):
        """登录网站"""
        print(f"\n正在访问登录页面: {self.base_url}")
        self.driver.get(self.base_url)
        time.sleep(3)
        
        try:
            # 保存登录页截图
            login_ss = os.path.join(self.output_dir, "00_login_page.png")
            self.driver.save_screenshot(login_ss)
            print(f"✓ 已保存登录页截图")
            
            # 查找并填写登录表单
            print("正在填写登录表单...")
            username_input = self.driver.find_element(By.NAME, "username")
            password_input = self.driver.find_element(By.NAME, "password")
            
            username_input.clear()
            username_input.send_keys(self.username)
            password_input.clear()
            password_input.send_keys(self.password)
            
            # 点击登录按钮
            login_button_selectors = [
                (By.XPATH, "//button[@type='button']"),
                (By.XPATH, "//button[contains(@class, 'el-button--primary')]"),
                (By.CSS_SELECTOR, "button.el-button--primary"),
                (By.XPATH, "//button"),
            ]
            
            login_button = None
            for selector_type, selector_value in login_button_selectors:
                try:
                    login_button = self.driver.find_element(selector_type, selector_value)
                    break
                except:
                    pass
            
            if login_button:
                login_button.click()
                print("✓ 已点击登录按钮")
            else:
                password_input.submit()
                print("✓ 已提交登录表单")
            
            # 等待页面跳转
            print("等待登录完成...")
            for i in range(10):
                time.sleep(1)
                current_url = self.driver.current_url
                if 'dashboard' in current_url or 'login' not in current_url:
                    print(f"✓ 登录成功！当前 URL: {current_url}")
                    break
            
            # 额外等待页面加载
            time.sleep(3)
            
            # 保存登录后截图
            after_login_ss = os.path.join(self.output_dir, "01_after_login.png")
            self.driver.save_screenshot(after_login_ss)
            print(f"✓ 已保存登录后截图")
            print(f"✓ 当前页面标题: {self.driver.title}")
            
            return True
            
        except Exception as e:
            print(f"✗ 登录失败: {str(e)}")
            return False
    
    def take_screenshot(self, name):
        """截取当前页面"""
        try:
            page_hash = self.get_page_hash()
            if page_hash in self.visited_views:
                return False
            
            self.visited_views.add(page_hash)
            
            # 等待页面稳定
            time.sleep(2)
            
            # 滚动页面
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
            
            # 生成文件名
            safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name)
            safe_name = safe_name.strip().replace(' ', '_')[:50]
            
            filename = f"{self.screenshot_index:03d}_{safe_name}_{page_hash[:8]}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            # 截图
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
    
    def get_all_menu_items(self):
        """获取所有菜单项（包括子菜单）"""
        menu_items = []
        
        try:
            time.sleep(2)
            
            # 查找所有一级菜单项
            # 尝试多种选择器
            parent_selectors = [
                "//li[contains(@class, 'el-submenu')]",
                "//li[contains(@class, 'el-menu-item')]",
                "//*[contains(@class, 'sidebar')]//li",
                "//*[contains(@class, 'menu')]//li[not(contains(@class, 'is-opened'))]",
            ]
            
            all_menu_elements = []
            for selector in parent_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    all_menu_elements.extend(elements)
                except:
                    pass
            
            # 去重
            seen_texts = set()
            for elem in all_menu_elements:
                try:
                    if elem.is_displayed():
                        # 获取菜单项文本（只获取直接子元素的文本）
                        text = elem.text.strip().split('\n')[0] if elem.text else ""
                        
                        if text and len(text) < 50 and text not in seen_texts:
                            seen_texts.add(text)
                            
                            # 检查是否有子菜单
                            is_submenu = 'el-submenu' in elem.get_attribute('class')
                            
                            menu_items.append({
                                'text': text,
                                'element': elem,
                                'is_submenu': is_submenu
                            })
                except:
                    pass
            
            print(f"✓ 发现 {len(menu_items)} 个菜单项")
            return menu_items
            
        except Exception as e:
            print(f"✗ 获取菜单项失败: {str(e)}")
            return []
    
    def get_submenu_items(self, parent_element):
        """获取子菜单项"""
        submenu_items = []
        
        try:
            # 查找父元素下的所有子菜单项
            time.sleep(1)
            
            # 尝试多种选择器查找子菜单
            submenu_selectors = [
                ".//ul[contains(@class, 'el-menu--inline')]//li",
                ".//ul[@role='menu']//li",
                ".//li[contains(@class, 'el-menu-item')]",
            ]
            
            for selector in submenu_selectors:
                try:
                    sub_elements = parent_element.find_elements(By.XPATH, selector)
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
                except:
                    pass
            
            # 去重
            seen = set()
            unique_items = []
            for item in submenu_items:
                if item['text'] not in seen:
                    seen.add(item['text'])
                    unique_items.append(item)
            
            return unique_items
            
        except Exception as e:
            print(f"    ✗ 获取子菜单失败: {str(e)}")
            return []
    
    def click_element(self, element):
        """尝试多种方式点击元素"""
        try:
            # 滚动到元素可见
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
            
            # 方法1: 直接点击
            try:
                element.click()
                return True
            except:
                pass
            
            # 方法2: JavaScript 点击
            try:
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except:
                pass
            
            # 方法3: Actions 点击
            try:
                ActionChains(self.driver).move_to_element(element).click().perform()
                return True
            except:
                pass
            
            return False
            
        except Exception as e:
            print(f"    ✗ 点击失败: {str(e)}")
            return False
    
    def explore_all_menus(self):
        """遍历所有菜单（包括子菜单）"""
        print("\n开始全面遍历菜单...")
        print("=" * 60)
        
        # 截取主页
        self.take_screenshot("主页_Dashboard")
        
        # 获取所有菜单项
        menu_items = self.get_all_menu_items()
        
        if not menu_items:
            print("⚠ 未找到菜单项")
            return
        
        # 遍历每个菜单项
        for i, item in enumerate(menu_items):
            try:
                print(f"\n[{i+1}/{len(menu_items)}] 正在处理: {item['text']}")
                
                # 重新查找元素（避免 stale element）
                time.sleep(1)
                fresh_menu_items = self.get_all_menu_items()
                
                # 找到对应的菜单项
                target_item = None
                for fresh_item in fresh_menu_items:
                    if fresh_item['text'] == item['text']:
                        target_item = fresh_item
                        break
                
                if not target_item:
                    print(f"  ⚠ 无法找到菜单项: {item['text']}")
                    continue
                
                # 检查是否是有子菜单的项
                if target_item['is_submenu']:
                    print(f"  → 这是一个包含子菜单的项")
                    
                    # 点击展开子菜单
                    if self.click_element(target_item['element']):
                        time.sleep(1.5)
                        
                        # 获取子菜单项
                        submenu_items = self.get_submenu_items(target_item['element'])
                        
                        if submenu_items:
                            print(f"  → 发现 {len(submenu_items)} 个子菜单项")
                            
                            # 遍历子菜单
                            for j, sub_item in enumerate(submenu_items):
                                try:
                                    print(f"    [{j+1}/{len(submenu_items)}] 子菜单: {sub_item['text']}")
                                    
                                    # 重新获取子菜单元素
                                    time.sleep(0.5)
                                    fresh_parent = None
                                    for fp in self.get_all_menu_items():
                                        if fp['text'] == item['text']:
                                            fresh_parent = fp['element']
                                            break
                                    
                                    if fresh_parent:
                                        fresh_subs = self.get_submenu_items(fresh_parent)
                                        for fs in fresh_subs:
                                            if fs['text'] == sub_item['text']:
                                                if self.click_element(fs['element']):
                                                    time.sleep(2)
                                                    self.take_screenshot(f"{item['text']} - {sub_item['text']}")
                                                break
                                
                                except Exception as e:
                                    print(f"    ✗ 处理子菜单出错: {str(e)}")
                        else:
                            print(f"  → 未找到子菜单，尝试截图当前页")
                            time.sleep(2)
                            self.take_screenshot(item['text'])
                    else:
                        print(f"  ✗ 无法点击菜单项")
                
                else:
                    # 普通菜单项（无子菜单）
                    if self.click_element(target_item['element']):
                        time.sleep(2)
                        self.take_screenshot(item['text'])
                    else:
                        print(f"  ✗ 无法点击菜单项")
                
            except Exception as e:
                print(f"  ✗ 处理菜单项出错: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "=" * 60)
        print(f"✓ 完成！共截图 {len(self.screenshots)} 个页面")
    
    def save_report(self):
        """保存报告"""
        # JSON 报告
        report_file = os.path.join(self.output_dir, "report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "base_url": self.base_url,
                "total_screenshots": len(self.screenshots),
                "screenshots": self.screenshots
            }, f, ensure_ascii=False, indent=2)
        
        # HTML 报告
        html_file = os.path.join(self.output_dir, "report.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>完整网站截图报告</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .info {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .screenshot-item {{
            background-color: white;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .screenshot-item h2 {{
            color: #4CAF50;
            margin-top: 0;
        }}
        .screenshot-item img {{
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-top: 10px;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .screenshot-item img:hover {{
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            transform: scale(1.01);
        }}
        .metadata {{
            background-color: #f9f9f9;
            padding: 10px;
            border-left: 4px solid #4CAF50;
            margin: 10px 0;
            font-size: 14px;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            flex: 1;
            text-align: center;
        }}
        .stat-number {{
            font-size: 36px;
            font-weight: bold;
        }}
        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
        }}
    </style>
</head>
<body>
    <h1>🖼️ 完整网站截图报告</h1>
    
    <div class="info">
        <p><strong>网站地址:</strong> {self.base_url}</p>
        <p><strong>生成时间:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number">{len(self.screenshots)}</div>
                <div class="stat-label">总截图数</div>
            </div>
        </div>
    </div>
""")
            
            for screenshot in self.screenshots:
                f.write(f"""
    <div class="screenshot-item">
        <h2>{screenshot['index']}. {screenshot['name']}</h2>
        <div class="metadata">
            <p><strong>页面标题:</strong> {screenshot['title']}</p>
            <p><strong>URL:</strong> {screenshot['url']}</p>
        </div>
        <img src="{screenshot['filename']}" alt="{screenshot['name']}" 
             onclick="window.open(this.src)" title="点击查看大图">
    </div>
""")
            
            f.write("""
</body>
</html>
""")
        
        print(f"\n✓ 已保存 JSON 报告: {report_file}")
        print(f"✓ 已保存 HTML 报告: {html_file}")
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()


def main():
    base_url = "https://jhtest.bjstarfish.com/"
    username = "admin"
    password = "123456"
    output_dir = "screenshots_complete"
    
    print("=" * 60)
    print("🚀 完整版自动化网站截图工具（包含所有子菜单）")
    print("=" * 60)
    print(f"📍 目标网站: {base_url}")
    print(f"👤 用户名: {username}")
    print(f"📁 输出目录: {output_dir}")
    print("=" * 60)
    
    screenshotter = None
    try:
        screenshotter = CompleteScreenshotter(base_url, username, password, output_dir)
        
        if screenshotter.login():
            screenshotter.explore_all_menus()
            screenshotter.save_report()
            
            print("\n" + "=" * 60)
            print("✅ 所有任务完成！")
            print(f"📁 截图已保存到: {os.path.abspath(output_dir)}")
            print(f"📊 共生成 {len(screenshotter.screenshots)} 张截图")
            print(f"📄 请打开 {os.path.join(output_dir, 'report.html')} 查看报告")
            print("=" * 60)
        else:
            print("\n❌ 登录失败")
    
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
