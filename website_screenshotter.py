#!/usr/bin/env python3
"""
自动化网站截图工具
访问指定网站，自动登录，遍历所有页面并截图
"""

import os
import time
import hashlib
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json


class WebsiteScreenshotter:
    def __init__(self, base_url, username, password, output_dir="screenshots"):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.output_dir = output_dir
        self.visited_urls = set()
        self.screenshots = []
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 配置 Chrome 选项
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--ignore-certificate-errors')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
    def get_url_hash(self, url):
        """生成URL的短哈希值作为文件名"""
        return hashlib.md5(url.encode()).hexdigest()[:8]
    
    def login(self):
        """登录网站"""
        print(f"正在访问登录页面: {self.base_url}")
        self.driver.get(self.base_url)
        time.sleep(2)
        
        try:
            # 尝试多种常见的登录表单元素定位方式
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 保存登录页面截图
            login_screenshot = os.path.join(self.output_dir, "00_login_page.png")
            self.driver.save_screenshot(login_screenshot)
            print(f"已保存登录页面截图: {login_screenshot}")
            
            # 尝试查找用户名输入框
            username_input = None
            password_input = None
            login_button = None
            
            # 尝试多种选择器查找用户名输入框
            username_selectors = [
                (By.NAME, "username"),
                (By.NAME, "user"),
                (By.NAME, "account"),
                (By.ID, "username"),
                (By.ID, "user"),
                (By.XPATH, "//input[@type='text']"),
                (By.XPATH, "//input[@placeholder='用户名']"),
                (By.XPATH, "//input[@placeholder='账号']"),
            ]
            
            for selector_type, selector_value in username_selectors:
                try:
                    username_input = self.driver.find_element(selector_type, selector_value)
                    print(f"找到用户名输入框: {selector_type}={selector_value}")
                    break
                except NoSuchElementException:
                    continue
            
            # 尝试多种选择器查找密码输入框
            password_selectors = [
                (By.NAME, "password"),
                (By.NAME, "pass"),
                (By.NAME, "pwd"),
                (By.ID, "password"),
                (By.ID, "pass"),
                (By.XPATH, "//input[@type='password']"),
            ]
            
            for selector_type, selector_value in password_selectors:
                try:
                    password_input = self.driver.find_element(selector_type, selector_value)
                    print(f"找到密码输入框: {selector_type}={selector_value}")
                    break
                except NoSuchElementException:
                    continue
            
            if not username_input or not password_input:
                print("警告: 无法找到登录表单元素，可能已经登录或页面结构不同")
                return True
            
            # 输入用户名和密码
            username_input.clear()
            username_input.send_keys(self.username)
            print(f"已输入用户名: {self.username}")
            
            password_input.clear()
            password_input.send_keys(self.password)
            print("已输入密码")
            
            # 查找登录按钮
            login_button_selectors = [
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button[contains(text(), '登录')]"),
                (By.XPATH, "//button[contains(text(), '登錄')]"),
                (By.XPATH, "//button[contains(text(), 'Login')]"),
                (By.XPATH, "//input[@type='submit']"),
                (By.XPATH, "//a[contains(text(), '登录')]"),
            ]
            
            for selector_type, selector_value in login_button_selectors:
                try:
                    login_button = self.driver.find_element(selector_type, selector_value)
                    print(f"找到登录按钮: {selector_type}={selector_value}")
                    break
                except NoSuchElementException:
                    continue
            
            if login_button:
                login_button.click()
                print("已点击登录按钮")
            else:
                # 如果找不到按钮，尝试提交表单
                password_input.submit()
                print("已提交登录表单")
            
            # 等待登录完成
            time.sleep(3)
            
            # 保存登录后页面截图
            after_login_screenshot = os.path.join(self.output_dir, "01_after_login.png")
            self.driver.save_screenshot(after_login_screenshot)
            print(f"已保存登录后页面截图: {after_login_screenshot}")
            
            print("登录成功！")
            return True
            
        except Exception as e:
            print(f"登录时出错: {str(e)}")
            error_screenshot = os.path.join(self.output_dir, "error_login.png")
            self.driver.save_screenshot(error_screenshot)
            print(f"已保存错误页面截图: {error_screenshot}")
            return False
    
    def get_all_links(self):
        """获取当前页面的所有链接"""
        links = set()
        try:
            # 等待 JavaScript 加载
            time.sleep(2)
            
            # 执行 JavaScript 获取所有可能的链接和可点击元素
            # 尝试展开所有菜单
            self.driver.execute_script("""
                // 尝试展开所有可能的菜单
                var menus = document.querySelectorAll('.el-menu, .menu, [role="menu"]');
                menus.forEach(function(menu) {
                    menu.style.display = 'block';
                });
                
                // 尝试展开所有下拉菜单
                var dropdowns = document.querySelectorAll('.dropdown, .el-dropdown');
                dropdowns.forEach(function(dropdown) {
                    dropdown.style.display = 'block';
                });
            """)
            time.sleep(1)
            
            # 获取所有 <a> 标签
            elements = self.driver.find_elements(By.TAG_NAME, "a")
            for element in elements:
                try:
                    href = element.get_attribute("href")
                    if href and href.startswith('http'):
                        # 转换为绝对URL
                        absolute_url = urljoin(self.driver.current_url, href)
                        # 只保留同域名的链接
                        if urlparse(absolute_url).netloc == urlparse(self.base_url).netloc:
                            # 移除锚点
                            clean_url = absolute_url.split('#')[0]
                            if clean_url:
                                links.add(clean_url)
                except:
                    continue
            
            # 查找可能有 @click 或其他事件的元素（Vue.js 应用）
            clickable_elements = self.driver.find_elements(By.XPATH, 
                "//*[@onclick or @click or contains(@class, 'menu') or contains(@class, 'nav')]")
            
            print(f"  找到 {len(elements)} 个 <a> 标签和 {len(clickable_elements)} 个可点击元素")
            
        except Exception as e:
            print(f"获取链接时出错: {str(e)}")
        
        return links
    
    def take_screenshot(self, url, index):
        """访问URL并截图"""
        if url in self.visited_urls:
            return False
        
        try:
            print(f"\n[{index}] 正在访问: {url}")
            self.driver.get(url)
            time.sleep(2)  # 等待页面加载
            
            # 滚动页面以加载动态内容
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(0.5)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
            
            # 生成文件名
            url_hash = self.get_url_hash(url)
            # 从URL提取路径作为描述
            path = urlparse(url).path.strip('/').replace('/', '_')
            if not path:
                path = "home"
            filename = f"{index:03d}_{path}_{url_hash}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            # 截图
            self.driver.save_screenshot(filepath)
            
            # 获取页面标题
            page_title = self.driver.title
            
            self.screenshots.append({
                "index": index,
                "url": url,
                "title": page_title,
                "filename": filename,
                "filepath": filepath
            })
            
            self.visited_urls.add(url)
            print(f"✓ 已保存截图: {filename}")
            print(f"  标题: {page_title}")
            
            return True
            
        except Exception as e:
            print(f"✗ 截图失败: {str(e)}")
            return False
    
    def crawl_and_screenshot(self, max_pages=50):
        """遍历网站并截图"""
        print("\n开始遍历网站并截图...")
        
        # 从首页开始
        urls_to_visit = [self.base_url]
        screenshot_index = 1
        
        while urls_to_visit and screenshot_index <= max_pages:
            current_url = urls_to_visit.pop(0)
            
            if current_url in self.visited_urls:
                continue
            
            # 访问并截图
            if self.take_screenshot(current_url, screenshot_index):
                screenshot_index += 1
                
                # 获取当前页面的所有链接
                new_links = self.get_all_links()
                
                # 添加未访问的链接到队列
                for link in new_links:
                    if link not in self.visited_urls and link not in urls_to_visit:
                        urls_to_visit.append(link)
                
                print(f"  发现 {len(new_links)} 个链接，队列中还有 {len(urls_to_visit)} 个待访问")
        
        print(f"\n遍历完成！共截图 {len(self.screenshots)} 个页面")
    
    def save_report(self):
        """保存截图报告"""
        report_file = os.path.join(self.output_dir, "report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "base_url": self.base_url,
                "total_screenshots": len(self.screenshots),
                "screenshots": self.screenshots
            }, f, ensure_ascii=False, indent=2)
        print(f"\n已保存报告: {report_file}")
        
        # 生成 Markdown 报告
        md_report_file = os.path.join(self.output_dir, "report.md")
        with open(md_report_file, 'w', encoding='utf-8') as f:
            f.write(f"# 网站截图报告\n\n")
            f.write(f"**网站地址**: {self.base_url}\n\n")
            f.write(f"**截图总数**: {len(self.screenshots)}\n\n")
            f.write(f"**生成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            for screenshot in self.screenshots:
                f.write(f"## {screenshot['index']}. {screenshot['title']}\n\n")
                f.write(f"**URL**: {screenshot['url']}\n\n")
                f.write(f"![{screenshot['title']}]({screenshot['filename']})\n\n")
                f.write("---\n\n")
        
        print(f"已保存 Markdown 报告: {md_report_file}")
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("\n浏览器已关闭")


def main():
    # 配置参数
    base_url = "https://jhtest.bjstarfish.com/"
    username = "admin"
    password = "123456"
    output_dir = "screenshots"
    max_pages = 50  # 最多截图50个页面
    
    print("=" * 60)
    print("自动化网站截图工具")
    print("=" * 60)
    print(f"目标网站: {base_url}")
    print(f"用户名: {username}")
    print(f"输出目录: {output_dir}")
    print(f"最大页面数: {max_pages}")
    print("=" * 60)
    
    screenshotter = None
    try:
        # 创建截图工具实例
        screenshotter = WebsiteScreenshotter(base_url, username, password, output_dir)
        
        # 登录
        if screenshotter.login():
            # 遍历并截图
            screenshotter.crawl_and_screenshot(max_pages=max_pages)
            
            # 保存报告
            screenshotter.save_report()
            
            print("\n" + "=" * 60)
            print("✓ 所有任务完成！")
            print(f"✓ 截图已保存到: {os.path.abspath(output_dir)}")
            print("=" * 60)
        else:
            print("\n✗ 登录失败，无法继续")
    
    except Exception as e:
        print(f"\n✗ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if screenshotter:
            screenshotter.close()


if __name__ == "__main__":
    main()
