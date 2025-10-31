#!/usr/bin/env python3
"""
调试票务系统登录
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

base_url = "https://xstest.axioxio.com/"
username = "13811458301"
password = "4<z%0/RS"

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(5)

try:
    print(f"访问: {base_url}")
    driver.get(base_url)
    time.sleep(5)
    
    print(f"当前URL: {driver.current_url}")
    print(f"页面标题: {driver.title}")
    
    # 保存登录前页面
    driver.save_screenshot("/workspace/debug_login_before.png")
    print("✓ 保存登录前截图")
    
    # 查找输入框
    print("\n查找输入框...")
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"找到 {len(inputs)} 个input元素")
    
    for i, inp in enumerate(inputs):
        print(f"  [{i}] type={inp.get_attribute('type')}, name={inp.get_attribute('name')}, placeholder={inp.get_attribute('placeholder')}")
    
    # 查找按钮
    print("\n查找按钮...")
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"找到 {len(buttons)} 个button元素")
    
    for i, btn in enumerate(buttons):
        print(f"  [{i}] text={btn.text}, type={btn.get_attribute('type')}")
    
    # 尝试登录
    print("\n尝试登录...")
    username_input = inputs[0]  # 第一个input
    password_input = inputs[1]  # 第二个input
    
    username_input.clear()
    username_input.send_keys(username)
    print(f"✓ 输入用户名: {username}")
    
    password_input.clear()
    password_input.send_keys(password)
    print(f"✓ 输入密码")
    
    time.sleep(1)
    
    # 点击登录按钮
    if buttons:
        buttons[0].click()
        print("✓ 点击登录按钮")
    
    # 等待跳转
    print("\n等待页面跳转...")
    for i in range(20):
        time.sleep(1)
        current_url = driver.current_url
        print(f"[{i+1}/20] URL: {current_url}")
        
        if 'login' not in current_url.lower():
            print(f"\n✓ 登录成功！")
            break
    
    time.sleep(3)
    
    # 保存登录后页面
    driver.save_screenshot("/workspace/debug_login_after.png")
    print(f"\n✓ 保存登录后截图")
    print(f"✓ 最终URL: {driver.current_url}")
    print(f"✓ 页面标题: {driver.title}")
    
    # 保存页面HTML
    with open("/workspace/debug_page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"✓ 保存页面HTML")

finally:
    driver.quit()
    print("\n浏览器已关闭")
