#!/usr/bin/env python3
"""
调试语言选择器
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
    
    driver.save_screenshot("/workspace/login_page_initial.png")
    print("✓ 初始登录页面截图")
    
    # 查找语言选择器
    print("\n查找语言选择器...")
    
    # 方法1: 查找包含语言文本的元素
    lang_elements = driver.find_elements(By.XPATH, 
        "//*[contains(text(), '中文')] | " +
        "//*[contains(text(), '简体')] | " +
        "//*[contains(text(), 'Chinese')] | " +
        "//*[contains(text(), 'CN')] | " +
        "//*[contains(text(), 'ZH')] | " +
        "//select[@name='language'] | " +
        "//select[contains(@class, 'language')] | " +
        "//*[contains(@class, 'language')] | " +
        "//*[contains(@class, 'lang')]")
    
    print(f"找到 {len(lang_elements)} 个可能的语言元素\n")
    
    for i, elem in enumerate(lang_elements[:10], 1):
        try:
            if elem.is_displayed():
                tag = elem.tag_name
                text = elem.text.strip()
                classes = elem.get_attribute('class')
                elem_id = elem.get_attribute('id')
                print(f"  [{i}] 标签: {tag}")
                print(f"      文本: {text[:50]}")
                print(f"      Class: {classes}")
                print(f"      ID: {elem_id}")
                print()
        except:
            pass
    
    # 查找下拉菜单
    print("\n查找所有下拉菜单...")
    selects = driver.find_elements(By.TAG_NAME, "select")
    print(f"找到 {len(selects)} 个select元素\n")
    
    for i, select in enumerate(selects, 1):
        try:
            if select.is_displayed():
                name = select.get_attribute('name')
                options = select.find_elements(By.TAG_NAME, "option")
                print(f"  Select[{i}] name: {name}")
                print(f"  选项数量: {len(options)}")
                for j, opt in enumerate(options[:5], 1):
                    print(f"    [{j}] {opt.text} (value={opt.get_attribute('value')})")
                print()
        except:
            pass
    
    # 查找按钮和链接
    print("\n查找可能的语言切换按钮...")
    buttons = driver.find_elements(By.XPATH, 
        "//button | //a[contains(@class, 'btn')] | //div[contains(@class, 'dropdown')]")
    
    for i, btn in enumerate(buttons[:20], 1):
        try:
            if btn.is_displayed():
                text = btn.text.strip()
                if any(keyword in text.upper() for keyword in ['CN', 'ZH', 'EN', 'LANG', '中文', 'CHINESE']):
                    print(f"  按钮[{i}]: {text}")
                    print(f"    Class: {btn.get_attribute('class')}")
        except:
            pass
    
    # 保存页面源码
    with open("/workspace/login_page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("\n✓ 页面源码已保存: login_page_source.html")
    
    # 尝试查找具体的语言选择器（常见的实现）
    print("\n尝试常见的语言选择器模式...")
    
    # 模式1: abp-language-switch
    try:
        lang_switch = driver.find_element(By.XPATH, "//*[contains(@class, 'language-switch')] | //*[@id='language-switch']")
        print(f"✓ 找到 language-switch: {lang_switch.text}")
    except:
        print("  未找到 language-switch")
    
    # 模式2: 图标按钮
    try:
        lang_icon = driver.find_element(By.XPATH, "//i[contains(@class, 'fa-language')] | //i[contains(@class, 'bi-translate')]")
        print(f"✓ 找到语言图标")
    except:
        print("  未找到语言图标")

finally:
    driver.quit()
