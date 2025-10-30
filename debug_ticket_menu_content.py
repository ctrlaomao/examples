#!/usr/bin/env python3
"""
调试票务系统菜单内容
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
    # 登录
    print("登录中...")
    driver.get("https://xstest.axioxio.com/")
    time.sleep(5)
    
    username_input = driver.find_element(By.NAME, "LoginInput.UserNameOrEmailAddress")
    password_input = driver.find_element(By.NAME, "LoginInput.Password")
    
    username_input.send_keys("13811458301")
    password_input.send_keys("4<z%0/RS")
    password_input.send_keys(Keys.RETURN)
    
    time.sleep(5)
    print(f"登录成功，URL: {driver.current_url}\n")
    
    # 获取页面HTML片段
    print("=" * 80)
    print("【主页内容】")
    print("=" * 80)
    
    # 查找主要内容区域
    try:
        main_content = driver.find_element(By.XPATH, "//main | //div[contains(@class, 'main')] | //div[contains(@class, 'content')]")
        print(f"主内容区域：\n{main_content.text[:500]}\n")
    except:
        print("未找到主内容区域")
    
    # 查找所有菜单
    print("=" * 80)
    print("【菜单结构】")
    print("=" * 80)
    
    menu_links = driver.find_elements(By.XPATH, "//nav//a | //aside//a | //*[contains(@class, 'sidebar')]//a")
    print(f"找到 {len(menu_links)} 个菜单链接\n")
    
    menus = []
    for i, link in enumerate(menu_links[:15], 1):
        try:
            if link.is_displayed():
                text = link.text.strip()
                href = link.get_attribute('href')
                if text:
                    print(f"  [{i}] {text}")
                    print(f"      href: {href}")
                    menus.append({'text': text, 'element': link})
        except:
            pass
    
    # 测试点击第一个菜单
    if len(menus) >= 2:
        print("\n" + "=" * 80)
        print(f"【点击测试】点击: {menus[1]['text']}")
        print("=" * 80)
        
        driver.get("https://xstest.axioxio.com/")
        time.sleep(3)
        
        # 重新查找元素
        test_menu = None
        fresh_links = driver.find_elements(By.XPATH, "//nav//a | //aside//a")
        for link in fresh_links:
            try:
                if link.is_displayed() and link.text.strip() == menus[1]['text']:
                    test_menu = link
                    break
            except:
                pass
        
        if test_menu:
            print(f"\n点击前URL: {driver.current_url}")
            
            driver.execute_script("arguments[0].click();", test_menu)
            time.sleep(3)
            
            print(f"点击后URL: {driver.current_url}")
            
            # 查找页面标题/面包屑
            try:
                breadcrumbs = driver.find_elements(By.XPATH, "//*[contains(@class, 'breadcrumb')] | //h1 | //h2 | //*[@class='page-title']")
                print("\n页面标题/面包屑:")
                for bc in breadcrumbs[:5]:
                    if bc.is_displayed() and bc.text.strip():
                        print(f"  - {bc.text.strip()}")
            except:
                pass
            
            # 查找页面按钮
            print("\n页面按钮:")
            buttons = driver.find_elements(By.XPATH, "//button | //a[contains(@class, 'btn')]")
            button_texts = []
            for btn in buttons[:20]:
                try:
                    if btn.is_displayed():
                        text = btn.text.strip()
                        if text and len(text) < 50:
                            button_texts.append(text)
                except:
                    pass
            
            for i, text in enumerate(set(button_texts), 1):
                print(f"  [{i}] {text}")
            
            # 查找表格
            print("\n表格:")
            tables = driver.find_elements(By.TAG_NAME, "table")
            print(f"  找到 {len(tables)} 个表格")
            
            if tables:
                try:
                    headers = tables[0].find_elements(By.TAG_NAME, "th")
                    print(f"  表头: {', '.join([h.text for h in headers[:10]])}")
                except:
                    pass
            
            # 截图
            driver.save_screenshot("/workspace/debug_menu_clicked.png")
            print("\n✓ 截图已保存: debug_menu_clicked.png")
            
            # 保存HTML
            with open("/workspace/debug_menu_clicked.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("✓ HTML已保存: debug_menu_clicked.html")
            
            # 查找是否有子菜单展开
            print("\n检查子菜单:")
            submenus = driver.find_elements(By.XPATH, 
                "//*[contains(@class, 'submenu')] | //*[contains(@class, 'sub-menu')] | //ul[contains(@class, 'menu')]//ul")
            print(f"  找到 {len(submenus)} 个可能的子菜单区域")
            
            for i, submenu in enumerate(submenus[:3], 1):
                try:
                    if submenu.is_displayed():
                        sub_links = submenu.find_elements(By.TAG_NAME, "a")
                        print(f"  子菜单[{i}]: {len(sub_links)} 个链接")
                        for link in sub_links[:5]:
                            if link.is_displayed():
                                print(f"    - {link.text.strip()}")
                except:
                    pass

finally:
    driver.quit()
