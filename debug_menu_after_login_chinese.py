#!/usr/bin/env python3
"""
调试登录后的中文菜单结构
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
    # 登录并切换语言
    driver.get("https://xstest.axioxio.com/")
    time.sleep(5)
    
    # 切换到中文
    lang_button = driver.find_element(By.XPATH, "//button[contains(@class, 'dropdown-toggle')]")
    lang_button.click()
    time.sleep(1)
    chinese_link = driver.find_element(By.XPATH, "//a[contains(text(), '简体中文')]")
    chinese_link.click()
    time.sleep(3)
    
    # 登录
    username_input = driver.find_element(By.NAME, "LoginInput.UserNameOrEmailAddress")
    password_input = driver.find_element(By.NAME, "LoginInput.Password")
    username_input.send_keys("13811458301")
    password_input.send_keys("4<z%0/RS")
    password_input.send_keys(Keys.RETURN)
    
    time.sleep(5)
    print(f"登录后URL: {driver.current_url}\n")
    
    # 展开所有子菜单
    driver.execute_script("""
        var innerMenus = document.querySelectorAll('.lpx-inner-menu');
        innerMenus.forEach(function(menu) {
            menu.classList.remove('collapsed');
            menu.style.display = 'block';
        });
    """)
    time.sleep(2)
    
    driver.save_screenshot("/workspace/debug_after_login_chinese.png")
    
    print("=" * 80)
    print("【侧边栏所有链接】")
    print("=" * 80)
    
    all_aside_links = driver.find_elements(By.XPATH, "//aside//a")
    print(f"总共找到 {len(all_aside_links)} 个链接\n")
    
    for i, link in enumerate(all_aside_links[:30], 1):
        try:
            text = link.text.strip()
            href = link.get_attribute('href')
            classes = link.get_attribute('class')
            
            # 检查是否在inner-menu中
            try:
                parent_ul = link.find_element(By.XPATH, "ancestor::ul[contains(@class, 'lpx-inner-menu')]")
                in_submenu = True
            except:
                in_submenu = False
            
            if text:
                print(f"[{i}] {text}")
                print(f"    href: {href}")
                print(f"    in_submenu: {in_submenu}")
                print(f"    classes: {classes}")
                print()
        except:
            pass
    
    # 保存HTML
    with open("/workspace/debug_menu_chinese.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("✓ HTML已保存: debug_menu_chinese.html")

finally:
    driver.quit()
