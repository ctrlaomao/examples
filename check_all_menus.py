#!/usr/bin/env python3
"""
检查票务系统所有菜单和功能
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
    print("=" * 80)
    print("检查票务系统所有菜单和功能")
    print("=" * 80)
    
    # 访问登录页
    driver.get("https://xstest.axioxio.com/")
    time.sleep(5)
    
    # 切换到简体中文
    print("\n切换到简体中文...")
    try:
        lang_button = driver.find_element(By.XPATH, "//button[contains(@class, 'dropdown-toggle')]")
        lang_button.click()
        time.sleep(1)
        
        chinese_link = driver.find_element(By.XPATH, "//a[contains(text(), '简体中文')]")
        chinese_link.click()
        time.sleep(3)
        print("✓ 已切换到简体中文")
    except:
        print("✗ 切换语言失败")
    
    # 登录
    print("\n登录系统...")
    username_input = driver.find_element(By.NAME, "LoginInput.UserNameOrEmailAddress")
    password_input = driver.find_element(By.NAME, "LoginInput.Password")
    
    username_input.send_keys("13811458301")
    password_input.send_keys("4<z%0/RS")
    password_input.send_keys(Keys.RETURN)
    
    time.sleep(5)
    print(f"✓ 登录成功，URL: {driver.current_url}")
    
    driver.save_screenshot("/workspace/homepage_chinese.png")
    
    # 获取所有一级菜单
    print("\n" + "=" * 80)
    print("【一级菜单列表】")
    print("=" * 80)
    
    time.sleep(2)
    
    # 使用JavaScript展开所有子菜单
    driver.execute_script("""
        var innerMenus = document.querySelectorAll('.lpx-inner-menu');
        innerMenus.forEach(function(menu) {
            menu.classList.remove('collapsed');
            menu.style.display = 'block';
        });
    """)
    time.sleep(2)
    
    # 查找所有菜单项
    all_menu_links = driver.find_elements(By.XPATH, "//aside//a | //nav//a")
    
    menus = {}
    current_parent = None
    
    for link in all_menu_links:
        try:
            if not link.is_displayed():
                continue
                
            text = link.text.strip()
            href = link.get_attribute('href')
            classes = link.get_attribute('class')
            
            if not text or len(text) > 100:
                continue
            
            # 判断是否是父菜单（有下拉箭头或包含特定class）
            parent_element = link.find_element(By.XPATH, "..")
            has_submenu = False
            try:
                parent_element.find_element(By.XPATH, ".//i[contains(@class, 'chevron')]")
                has_submenu = True
            except:
                pass
            
            # 判断是否在子菜单中
            is_in_submenu = 'lpx-inner-menu' in link.find_element(By.XPATH, "../..").get_attribute('class')
            
            if has_submenu and not is_in_submenu:
                # 这是一个父菜单
                current_parent = text
                if current_parent not in menus:
                    menus[current_parent] = {
                        'href': href,
                        'submenus': []
                    }
            elif is_in_submenu and current_parent:
                # 这是一个子菜单
                if text not in menus[current_parent]['submenus']:
                    menus[current_parent]['submenus'].append({
                        'text': text,
                        'href': href
                    })
            elif not is_in_submenu:
                # 这是一个没有子菜单的独立菜单
                if text not in menus:
                    menus[text] = {
                        'href': href,
                        'submenus': []
                    }
        except Exception as e:
            pass
    
    # 打印菜单结构
    total_pages = 0
    for i, (parent, data) in enumerate(menus.items(), 1):
        if data['submenus']:
            print(f"\n[{i}] {parent} (有 {len(data['submenus'])} 个子菜单)")
            for j, sub in enumerate(data['submenus'], 1):
                print(f"    [{i}.{j}] {sub['text']}")
                print(f"          URL: {sub['href']}")
                total_pages += 1
        else:
            print(f"\n[{i}] {parent} (无子菜单)")
            print(f"    URL: {data['href']}")
            total_pages += 1
    
    print("\n" + "=" * 80)
    print(f"统计：共 {len(menus)} 个一级菜单，{total_pages} 个页面")
    print("=" * 80)
    
    # 保存详细的菜单结构
    import json
    with open("/workspace/all_menus_structure.json", "w", encoding="utf-8") as f:
        json.dump(menus, f, ensure_ascii=False, indent=2)
    print("\n✓ 菜单结构已保存: all_menus_structure.json")

finally:
    driver.quit()
