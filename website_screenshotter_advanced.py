#!/usr/bin/env python3
"""
高级自动化网站截图工具 - 专为管理后台设计
支持单页应用（SPA）和动态菜单
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


class AdvancedWebsiteScreenshotter:
    def __init__(self, base_url, username, password, output_dir="screenshots"):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.output_dir = output_dir
        self.visited_views = set()
        self.screenshots = []
        self.screenshot_index = 1
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 配置 Chrome 选项
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--ignore-certificate-errors')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(5)
        
    def get_page_state_hash(self):
        """获取当前页面状态的哈希值（用于去重）"""
        try:
            # 使用 URL 和页面主要内容生成哈希
            url = self.driver.current_url
            title = self.driver.title
            # 获取主要内容区域的文本
            body_text = self.driver.find_element(By.TAG_NAME, "body").text[:500]
            state = f"{url}|{title}|{body_text}"
            return hashlib.md5(state.encode()).hexdigest()
        except:
            return hashlib.md5(str(time.time()).encode()).hexdigest()
    
    def login(self):
        """登录网站"""
        print(f"正在访问登录页面: {self.base_url}")
        self.driver.get(self.base_url)
        time.sleep(3)
        
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 保存登录页面截图
            login_screenshot = os.path.join(self.output_dir, "00_login_page.png")
            self.driver.save_screenshot(login_screenshot)
            print(f"✓ 已保存登录页面截图")
            
            # 查找用户名输入框
            username_input = None
            password_input = None
            
            username_selectors = [
                (By.NAME, "username"), (By.NAME, "user"), (By.NAME, "account"),
                (By.ID, "username"), (By.ID, "user"),
                (By.XPATH, "//input[@type='text']"),
                (By.XPATH, "//input[@placeholder='用户名']"),
                (By.XPATH, "//input[@placeholder='账号']"),
            ]
            
            for selector_type, selector_value in username_selectors:
                try:
                    username_input = self.driver.find_element(selector_type, selector_value)
                    break
                except NoSuchElementException:
                    continue
            
            password_selectors = [
                (By.NAME, "password"), (By.NAME, "pass"), (By.NAME, "pwd"),
                (By.ID, "password"), (By.ID, "pass"),
                (By.XPATH, "//input[@type='password']"),
            ]
            
            for selector_type, selector_value in password_selectors:
                try:
                    password_input = self.driver.find_element(selector_type, selector_value)
                    break
                except NoSuchElementException:
                    continue
            
            if not username_input or not password_input:
                print("⚠ 无法找到登录表单元素")
                return True
            
            # 输入用户名和密码
            username_input.clear()
            username_input.send_keys(self.username)
            password_input.clear()
            password_input.send_keys(self.password)
            
            # 查找并点击登录按钮
            login_button_selectors = [
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button[contains(text(), '登录')]"),
                (By.XPATH, "//button[contains(text(), 'Login')]"),
                (By.XPATH, "//input[@type='submit']"),
            ]
            
            login_button = None
            for selector_type, selector_value in login_button_selectors:
                try:
                    login_button = self.driver.find_element(selector_type, selector_value)
                    break
                except NoSuchElementException:
                    continue
            
            if login_button:
                login_button.click()
            else:
                password_input.submit()
            
            # 等待登录完成
            time.sleep(3)
            
            # 保存登录后页面截图
            after_login_screenshot = os.path.join(self.output_dir, "01_after_login.png")
            self.driver.save_screenshot(after_login_screenshot)
            print(f"✓ 已保存登录后页面截图")
            print(f"✓ 登录成功！当前页面: {self.driver.title}")
            
            return True
            
        except Exception as e:
            print(f"✗ 登录时出错: {str(e)}")
            return False
    
    def find_menu_items(self):
        """查找所有菜单项"""
        menu_items = []
        
        try:
            # 等待页面加载
            time.sleep(2)
            
            # 常见的菜单选择器
            menu_selectors = [
                "//nav//a",
                "//aside//a",
                "//*[contains(@class, 'menu')]//a",
                "//*[contains(@class, 'nav')]//a",
                "//*[contains(@class, 'sidebar')]//a",
                "//ul[contains(@class, 'el-menu')]//li",
                "//li[contains(@class, 'el-menu-item')]",
                "//*[@role='menuitem']",
                "//div[contains(@class, 'menu')]//div[contains(@class, 'item')]",
            ]
            
            for selector in menu_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        try:
                            if element.is_displayed() and element.is_enabled():
                                text = element.text.strip()
                                if text and len(text) < 50:  # 过滤过长的文本
                                    menu_items.append({
                                        'element': element,
                                        'text': text,
                                        'selector': selector
                                    })
                        except (StaleElementReferenceException, Exception):
                            continue
                except Exception:
                    continue
            
            # 去重（基于文本）
            seen_texts = set()
            unique_items = []
            for item in menu_items:
                if item['text'] not in seen_texts:
                    seen_texts.add(item['text'])
                    unique_items.append(item)
            
            print(f"  发现 {len(unique_items)} 个菜单项")
            
            return unique_items
            
        except Exception as e:
            print(f"  查找菜单项时出错: {str(e)}")
            return []
    
    def take_screenshot_with_name(self, name):
        """截取当前页面并保存"""
        try:
            # 检查是否已访问过相同的视图
            page_hash = self.get_page_state_hash()
            if page_hash in self.visited_views:
                return False
            
            self.visited_views.add(page_hash)
            
            # 等待页面加载
            time.sleep(2)
            
            # 滚动页面以加载动态内容
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(0.5)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
            
            # 生成文件名
            safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name)
            safe_name = safe_name.strip().replace(' ', '_')[:50]
            
            filename = f"{self.screenshot_index:03d}_{safe_name}_{page_hash[:8]}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            # 截图
            self.driver.save_screenshot(filepath)
            
            # 获取页面信息
            page_title = self.driver.title
            current_url = self.driver.current_url
            
            self.screenshots.append({
                "index": self.screenshot_index,
                "name": name,
                "url": current_url,
                "title": page_title,
                "filename": filename,
                "filepath": filepath
            })
            
            print(f"  [{self.screenshot_index:03d}] ✓ {name} - {page_title}")
            self.screenshot_index += 1
            
            return True
            
        except Exception as e:
            print(f"  ✗ 截图失败: {str(e)}")
            return False
    
    def explore_and_screenshot(self, max_screenshots=50):
        """智能探索并截图"""
        print("\n开始智能探索和截图...")
        print("=" * 60)
        
        # 截取主页
        self.take_screenshot_with_name("主页")
        
        # 查找所有菜单项
        menu_items = self.find_menu_items()
        
        if not menu_items:
            print("⚠ 未找到菜单项，尝试使用其他方法...")
            # 如果找不到菜单，尝试截取当前页面的不同状态
            return
        
        # 遍历每个菜单项
        for i, item in enumerate(menu_items):
            if self.screenshot_index > max_screenshots:
                print(f"\n已达到最大截图数量限制 ({max_screenshots})")
                break
            
            try:
                print(f"\n正在处理菜单项: {item['text']}")
                
                # 重新查找元素（避免 stale element）
                time.sleep(1)
                menu_items_fresh = self.find_menu_items()
                
                # 找到对应的菜单项
                target_item = None
                for fresh_item in menu_items_fresh:
                    if fresh_item['text'] == item['text']:
                        target_item = fresh_item
                        break
                
                if not target_item:
                    print(f"  ⚠ 无法找到菜单项: {item['text']}")
                    continue
                
                # 滚动到元素可见
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", 
                                          target_item['element'])
                time.sleep(0.5)
                
                # 尝试点击
                try:
                    # 方法1: 直接点击
                    target_item['element'].click()
                except Exception as e1:
                    try:
                        # 方法2: JavaScript 点击
                        self.driver.execute_script("arguments[0].click();", target_item['element'])
                    except Exception as e2:
                        try:
                            # 方法3: Actions 点击
                            ActionChains(self.driver).move_to_element(target_item['element']).click().perform()
                        except Exception as e3:
                            print(f"  ✗ 无法点击菜单项: {str(e3)}")
                            continue
                
                # 等待页面响应
                time.sleep(2)
                
                # 截图
                self.take_screenshot_with_name(item['text'])
                
                # 检查是否有子菜单
                try:
                    sub_menus = self.driver.find_elements(By.XPATH, 
                        f"//li[contains(@class, 'el-submenu') or contains(@class, 'submenu')]//li")
                    
                    if sub_menus:
                        print(f"  发现 {len(sub_menus)} 个子菜单")
                        for sub_menu in sub_menus[:10]:  # 限制子菜单数量
                            try:
                                if sub_menu.is_displayed():
                                    sub_text = sub_menu.text.strip()
                                    if sub_text and len(sub_text) < 50:
                                        sub_menu.click()
                                        time.sleep(2)
                                        self.take_screenshot_with_name(f"{item['text']} - {sub_text}")
                            except:
                                continue
                except:
                    pass
                
            except Exception as e:
                print(f"  ✗ 处理菜单项时出错: {str(e)}")
                continue
        
        print("\n" + "=" * 60)
        print(f"探索完成！共截图 {len(self.screenshots)} 个页面")
    
    def save_report(self):
        """保存截图报告"""
        # JSON 报告
        report_file = os.path.join(self.output_dir, "report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "base_url": self.base_url,
                "total_screenshots": len(self.screenshots),
                "screenshots": self.screenshots
            }, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 已保存 JSON 报告: {report_file}")
        
        # Markdown 报告
        md_report_file = os.path.join(self.output_dir, "report.md")
        with open(md_report_file, 'w', encoding='utf-8') as f:
            f.write(f"# 网站截图报告\n\n")
            f.write(f"**网站地址**: {self.base_url}\n\n")
            f.write(f"**截图总数**: {len(self.screenshots)}\n\n")
            f.write(f"**生成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            for screenshot in self.screenshots:
                f.write(f"## {screenshot['index']}. {screenshot['name']}\n\n")
                f.write(f"**页面标题**: {screenshot['title']}\n\n")
                f.write(f"**URL**: {screenshot['url']}\n\n")
                f.write(f"![{screenshot['name']}]({screenshot['filename']})\n\n")
                f.write("---\n\n")
        
        print(f"✓ 已保存 Markdown 报告: {md_report_file}")
        
        # HTML 报告
        html_report_file = os.path.join(self.output_dir, "report.html")
        with open(html_report_file, 'w', encoding='utf-8') as f:
            f.write(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>网站截图报告</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
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
        }}
        .metadata {{
            background-color: #f9f9f9;
            padding: 10px;
            border-left: 4px solid #4CAF50;
            margin: 10px 0;
        }}
        .metadata p {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <h1>🖼️ 网站截图报告</h1>
    
    <div class="info">
        <p><strong>网站地址:</strong> {self.base_url}</p>
        <p><strong>截图总数:</strong> {len(self.screenshots)}</p>
        <p><strong>生成时间:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
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
        <img src="{screenshot['filename']}" alt="{screenshot['name']}" loading="lazy">
    </div>
""")
            
            f.write("""
</body>
</html>
""")
        
        print(f"✓ 已保存 HTML 报告: {html_report_file}")
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()


def main():
    # 配置参数
    base_url = "https://jhtest.bjstarfish.com/"
    username = "admin"
    password = "123456"
    output_dir = "screenshots"
    max_screenshots = 50
    
    print("=" * 60)
    print("🚀 高级自动化网站截图工具")
    print("=" * 60)
    print(f"📍 目标网站: {base_url}")
    print(f"👤 用户名: {username}")
    print(f"📁 输出目录: {output_dir}")
    print(f"📊 最大截图数: {max_screenshots}")
    print("=" * 60)
    
    screenshotter = None
    try:
        screenshotter = AdvancedWebsiteScreenshotter(base_url, username, password, output_dir)
        
        if screenshotter.login():
            screenshotter.explore_and_screenshot(max_screenshots=max_screenshots)
            screenshotter.save_report()
            
            print("\n" + "=" * 60)
            print("✅ 所有任务完成！")
            print(f"📁 截图已保存到: {os.path.abspath(output_dir)}")
            print(f"📊 共生成 {len(screenshotter.screenshots)} 张截图")
            print("=" * 60)
        else:
            print("\n❌ 登录失败，无法继续")
    
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if screenshotter:
            screenshotter.close()
            print("\n🔚 浏览器已关闭")


if __name__ == "__main__":
    main()
