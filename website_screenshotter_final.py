#!/usr/bin/env python3
"""
最终版自动化网站截图工具 - 针对单页应用优化
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


class SPAScreenshotter:
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
            
            # 等待页面跳转（等待 URL 变化）
            print("等待登录完成...")
            for i in range(10):
                time.sleep(1)
                current_url = self.driver.current_url
                if 'dashboard' in current_url or 'login' not in current_url:
                    print(f"✓ 登录成功！当前 URL: {current_url}")
                    break
                print(f"  等待中... ({i+1}/10)")
            
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
    
    def find_and_click_menu_items(self):
        """查找并点击所有菜单项"""
        print("\n开始查找菜单项...")
        print("=" * 60)
        
        # 截取主页
        self.take_screenshot("主页_Dashboard")
        
        # 查找所有可能的菜单项选择器
        menu_selectors = [
            "//li[contains(@class, 'el-menu-item')]",
            "//div[contains(@class, 'el-menu-item')]",
            "//li[contains(@class, 'el-submenu')]",
            "//*[contains(@class, 'menu')]//li",
            "//*[contains(@class, 'sidebar')]//li",
            "//nav//li",
            "//aside//li",
        ]
        
        menu_items = []
        for selector in menu_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for elem in elements:
                    try:
                        if elem.is_displayed():
                            text = elem.text.strip()
                            if text and len(text) < 50 and text not in [item['text'] for item in menu_items]:
                                menu_items.append({
                                    'text': text,
                                    'selector': selector
                                })
                    except:
                        pass
            except:
                pass
        
        print(f"✓ 发现 {len(menu_items)} 个菜单项")
        
        if not menu_items:
            print("⚠ 未找到菜单项，尝试查找所有可点击元素...")
            # 尝试查找任何可点击的元素
            clickable_elements = self.driver.find_elements(By.XPATH, 
                "//*[@onclick or @click or contains(@class, 'clickable') or contains(@class, 'item')]")
            
            for elem in clickable_elements:
                try:
                    if elem.is_displayed():
                        text = elem.text.strip()
                        if text and len(text) < 50:
                            menu_items.append({'text': text, 'selector': 'clickable'})
                except:
                    pass
            
            print(f"✓ 找到 {len(menu_items)} 个可点击元素")
        
        # 遍历并点击每个菜单项
        for item in menu_items:
            try:
                print(f"\n正在处理: {item['text']}")
                
                # 重新查找元素
                time.sleep(1)
                found = False
                
                for selector in menu_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        for elem in elements:
                            if elem.is_displayed() and elem.text.strip() == item['text']:
                                # 滚动到元素
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                                time.sleep(0.5)
                                
                                # 点击
                                try:
                                    elem.click()
                                except:
                                    self.driver.execute_script("arguments[0].click();", elem)
                                
                                found = True
                                break
                        if found:
                            break
                    except:
                        pass
                
                if not found:
                    print(f"  ⚠ 无法点击菜单项")
                    continue
                
                # 等待页面响应
                time.sleep(2)
                
                # 截图
                self.take_screenshot(item['text'])
                
            except Exception as e:
                print(f"  ✗ 处理菜单项出错: {str(e)}")
        
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
    <title>网站截图报告</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
        }}
        .screenshot-item img:hover {{
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        .metadata {{
            background-color: #f9f9f9;
            padding: 10px;
            border-left: 4px solid #4CAF50;
            margin: 10px 0;
            font-size: 14px;
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
    output_dir = "screenshots"
    
    print("=" * 60)
    print("🚀 自动化网站截图工具")
    print("=" * 60)
    print(f"📍 目标网站: {base_url}")
    print(f"👤 用户名: {username}")
    print(f"📁 输出目录: {output_dir}")
    print("=" * 60)
    
    screenshotter = None
    try:
        screenshotter = SPAScreenshotter(base_url, username, password, output_dir)
        
        if screenshotter.login():
            screenshotter.find_and_click_menu_items()
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
