#!/usr/bin/env python3
"""
测试语言切换
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(options=chrome_options)

try:
    print("访问登录页面...")
    driver.get("https://xstest.axioxio.com/")
    time.sleep(5)
    
    driver.save_screenshot("/workspace/lang_step1_english.png")
    print("✓ 英文版登录页")
    
    # 查找语言下拉按钮
    print("\n点击语言下拉菜单...")
    lang_button = driver.find_element(By.XPATH, "//button[contains(@class, 'dropdown-toggle')]")
    lang_button.click()
    time.sleep(2)
    
    driver.save_screenshot("/workspace/lang_step2_dropdown.png")
    print("✓ 展开语言菜单")
    
    # 查找所有语言选项
    print("\n可用语言选项:")
    lang_options = driver.find_elements(By.XPATH, "//div[contains(@class, 'dropdown-menu')]//a | //ul[contains(@class, 'dropdown-menu')]//a")
    
    for i, option in enumerate(lang_options, 1):
        try:
            if option.is_displayed():
                text = option.text.strip()
                print(f"  [{i}] {text}")
        except:
            pass
    
    # 点击中文选项
    print("\n切换到简体中文...")
    chinese_options = driver.find_elements(By.XPATH, 
        "//a[contains(text(), '简体中文')] | " +
        "//a[contains(text(), '中文')] | " +
        "//a[contains(text(), 'Chinese')] | " +
        "//a[contains(@data-language, 'zh')] | " +
        "//a[contains(@href, 'zh-Hans')]")
    
    if chinese_options:
        for opt in chinese_options:
            if opt.is_displayed():
                print(f"✓ 找到中文选项: {opt.text}")
                opt.click()
                break
        
        time.sleep(3)
        driver.save_screenshot("/workspace/lang_step3_chinese.png")
        print("✓ 已切换到中文")
        
        # 检查页面文本
        page_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"\n页面文本预览:\n{page_text[:200]}")
    else:
        print("✗ 未找到中文选项")

finally:
    driver.quit()
