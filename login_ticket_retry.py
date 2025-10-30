#!/usr/bin/env python3
"""
重新尝试票务系统登录 - 多种方法
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

base_url = "https://xstest.axioxio.com/"
username = "13811458301"
password = "4<z%0/RS"

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(options=chrome_options)

try:
    print("=" * 80)
    print("尝试登录票务系统（多种方法）")
    print("=" * 80)
    
    print(f"\n访问: {base_url}")
    driver.get(base_url)
    time.sleep(5)
    
    print(f"当前URL: {driver.current_url}")
    driver.save_screenshot("/workspace/step1_initial.png")
    
    # 方法1：使用name属性
    print("\n【方法1】使用name属性定位")
    try:
        username_input = driver.find_element(By.NAME, "LoginInput.UserNameOrEmailAddress")
        password_input = driver.find_element(By.NAME, "LoginInput.Password")
        
        username_input.clear()
        username_input.send_keys(username)
        print(f"✓ 输入用户名: {username}")
        
        password_input.clear()
        password_input.send_keys(password)
        print(f"✓ 输入密码")
        
        time.sleep(1)
        driver.save_screenshot("/workspace/step2_filled.png")
        
        # 尝试多种提交方式
        
        # 方式A: 点击Login按钮
        print("\n尝试点击Login按钮...")
        login_buttons = driver.find_elements(By.XPATH, "//button[@type='submit']")
        if login_buttons:
            login_buttons[0].click()
            print("✓ 点击了submit按钮")
        
        time.sleep(3)
        driver.save_screenshot("/workspace/step3_after_click.png")
        
        # 检查URL是否变化
        current_url = driver.current_url
        print(f"点击后URL: {current_url}")
        
        # 如果还在登录页，尝试其他方法
        if 'login' in current_url.lower():
            print("\n还在登录页，尝试使用Enter键提交...")
            
            # 重新填写
            username_input = driver.find_element(By.NAME, "LoginInput.UserNameOrEmailAddress")
            password_input = driver.find_element(By.NAME, "LoginInput.Password")
            
            username_input.clear()
            username_input.send_keys(username)
            password_input.clear()
            password_input.send_keys(password)
            
            # 使用Enter键提交
            password_input.send_keys(Keys.RETURN)
            print("✓ 使用Enter键提交")
            
            time.sleep(3)
            driver.save_screenshot("/workspace/step4_after_enter.png")
        
        # 等待页面跳转
        print("\n等待登录完成...")
        for i in range(15):
            time.sleep(1)
            current_url = driver.current_url
            page_title = driver.title
            
            print(f"  [{i+1}/15] URL: {current_url[:80]}")
            
            # 检查是否跳转成功
            if 'login' not in current_url.lower() and current_url != base_url + "Account/Login?ReturnUrl=%2F":
                print(f"\n✓✓✓ 登录成功！")
                print(f"✓ 当前URL: {current_url}")
                print(f"✓ 页面标题: {page_title}")
                break
            
            # 检查是否有错误提示
            try:
                error_elements = driver.find_elements(By.XPATH, 
                    "//*[contains(@class, 'alert') or contains(@class, 'error') or contains(@class, 'invalid')]")
                for elem in error_elements:
                    if elem.is_displayed():
                        error_text = elem.text
                        if error_text:
                            print(f"  ⚠ 发现错误提示: {error_text}")
            except:
                pass
        
        time.sleep(3)
        
        # 最终状态
        print(f"\n最终URL: {driver.current_url}")
        print(f"最终标题: {driver.title}")
        driver.save_screenshot("/workspace/final_state.png")
        
        # 检查是否有导航菜单（说明已登录）
        print("\n检查是否已登录...")
        nav_elements = driver.find_elements(By.XPATH, "//nav | //aside | //*[contains(@class, 'menu')] | //*[contains(@class, 'sidebar')]")
        print(f"找到导航元素: {len(nav_elements)} 个")
        
        if nav_elements:
            print("✓ 发现导航菜单，可能已登录！")
            for i, nav in enumerate(nav_elements[:3]):
                print(f"  导航[{i}]: {nav.text[:100]}")
        
        # 查找所有链接
        links = driver.find_elements(By.TAG_NAME, "a")
        visible_links = [link for link in links if link.is_displayed()]
        print(f"\n页面可见链接: {len(visible_links)} 个")
        for i, link in enumerate(visible_links[:10]):
            try:
                print(f"  链接[{i}]: {link.text[:50]}")
            except:
                pass
        
    except Exception as e:
        print(f"\n✗ 登录失败: {str(e)}")
        import traceback
        traceback.print_exc()

finally:
    driver.quit()
    print("\n浏览器已关闭")
