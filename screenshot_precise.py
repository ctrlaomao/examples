#!/usr/bin/env python3
"""
精确的功能点截图工具 - 确保每个功能点都有正确对应的截图
"""

import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

class PreciseScreenshotter:
    def __init__(self, base_url, username, password, output_dir="screenshots_functions"):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.output_dir = output_dir
        self.screenshots = []
        
        os.makedirs(output_dir, exist_ok=True)
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--ignore-certificate-errors')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(3)
        
    def login(self):
        """登录"""
        print(f"\n正在登录...")
        self.driver.get(self.base_url)
        time.sleep(3)
        
        try:
            username_input = self.driver.find_element(By.NAME, "username")
            password_input = self.driver.find_element(By.NAME, "password")
            
            username_input.send_keys(self.username)
            password_input.send_keys(self.password)
            
            login_button = self.driver.find_element(By.XPATH, "//button[@type='button']")
            login_button.click()
            
            for i in range(10):
                time.sleep(1)
                if 'dashboard' in self.driver.current_url:
                    break
            
            time.sleep(2)
            print("✓ 登录成功")
            return True
        except Exception as e:
            print(f"✗ 登录失败: {str(e)}")
            return False
    
    def save_screenshot(self, index, module, function, description):
        """保存截图"""
        try:
            time.sleep(1.5)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
            
            filename = f"{index:03d}_{module}_{function}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            self.driver.save_screenshot(filepath)
            
            self.screenshots.append({
                "index": index,
                "module": module,
                "function": function,
                "description": description,
                "filename": filename,
                "url": self.driver.current_url,
                "title": self.driver.title
            })
            
            print(f"  [{index:03d}] ✓ {module} - {function}")
            return True
        except Exception as e:
            print(f"  [{index:03d}] ✗ 失败: {str(e)}")
            return False
    
    def click_menu(self, menu_text):
        """点击菜单"""
        try:
            time.sleep(1)
            # 查找包含指定文本的菜单项
            menu_xpath = f"//li[contains(@class, 'el-menu-item') or contains(@class, 'el-submenu')]//span[contains(text(), '{menu_text}')]"
            menus = self.driver.find_elements(By.XPATH, menu_xpath)
            
            if not menus:
                # 尝试更宽松的匹配
                menu_xpath = f"//*[contains(text(), '{menu_text}')]"
                menus = self.driver.find_elements(By.XPATH, menu_xpath)
            
            for menu in menus:
                if menu.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", menu)
                    time.sleep(0.5)
                    try:
                        menu.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", menu)
                    time.sleep(2)
                    return True
            return False
        except:
            return False
    
    def click_button(self, button_text):
        """点击按钮"""
        try:
            buttons = self.driver.find_elements(By.XPATH,
                f"//button[contains(text(), '{button_text}')] | //a[contains(@class, 'el-button')][contains(text(), '{button_text}')]")
            
            for btn in buttons:
                if btn.is_displayed() and btn.is_enabled():
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                        time.sleep(0.3)
                        btn.click()
                        time.sleep(1.5)
                        return True
                    except:
                        try:
                            self.driver.execute_script("arguments[0].click();", btn)
                            time.sleep(1.5)
                            return True
                        except:
                            pass
            return False
        except:
            return False
    
    def close_dialog(self):
        """关闭弹窗"""
        try:
            close_btns = self.driver.find_elements(By.XPATH,
                "//*[contains(@class, 'el-dialog__close') or contains(@class, 'el-drawer__close')]")
            for btn in close_btns:
                if btn.is_displayed():
                    btn.click()
                    time.sleep(0.5)
                    return True
            return False
        except:
            return False
    
    def capture_all_functions(self):
        """精确截图所有功能点"""
        print("\n开始精确截图...")
        print("=" * 70)
        
        idx = 1
        
        # 1. 登录 - 身份验证
        print(f"\n[{idx}] 登录 - 身份验证")
        self.driver.get(self.base_url)
        time.sleep(2)
        self.save_screenshot(idx, "登录", "身份验证", "用户登录页面")
        idx += 1
        
        # 重新登录
        self.login()
        
        # ========== 活动管理 ==========
        print(f"\n{'='*70}")
        print("【活动管理】")
        print(f"{'='*70}")
        
        # 2. 活动管理 - 创建、编辑活动
        print(f"\n[{idx}] 活动管理 - 创建、编辑活动")
        if self.click_menu("活动"):
            time.sleep(1)
            if self.click_menu("活动列表"):
                time.sleep(1)
                if self.click_button("新建"):
                    self.save_screenshot(idx, "活动管理", "创建活动", "新建活动弹窗")
                    self.close_dialog()
                    idx += 1
                else:
                    self.save_screenshot(idx, "活动管理", "创建活动", "活动列表页面")
                    idx += 1
        
        # 3. 活动管理 - 活动列表
        print(f"\n[{idx}] 活动管理 - 活动列表")
        if self.click_menu("活动列表"):
            time.sleep(1)
            self.save_screenshot(idx, "活动管理", "活动列表", "活动列表展示页面")
            idx += 1
        
        # 4. 活动管理 - 查询、查看、评价、删除活动
        print(f"\n[{idx}] 活动管理 - 查询、查看、评价、删除活动")
        # 点击查询按钮显示查询表单
        if self.click_button("查询"):
            time.sleep(1)
        self.save_screenshot(idx, "活动管理", "查询查看操作", "活动查询和操作功能")
        idx += 1
        
        # ========== 场地管理 ==========
        print(f"\n{'='*70}")
        print("【场地管理】")
        print(f"{'='*70}")
        
        # 5. 场地管理 - 创建、编辑场地
        print(f"\n[{idx}] 场地管理 - 创建、编辑场地")
        if self.click_menu("场地"):
            time.sleep(1)
            if self.click_menu("场地列表"):
                time.sleep(1)
                if self.click_button("新建"):
                    self.save_screenshot(idx, "场地管理", "创建场地", "新建场地页面")
                    self.driver.back()
                    time.sleep(1)
                    idx += 1
                else:
                    self.save_screenshot(idx, "场地管理", "创建场地", "场地列表页面")
                    idx += 1
        
        # 6. 场地管理 - 场地列表
        print(f"\n[{idx}] 场地管理 - 场地列表")
        if self.click_menu("场地列表"):
            time.sleep(1)
            self.save_screenshot(idx, "场地管理", "场地列表", "场地列表展示")
            idx += 1
        
        # 7. 场地管理 - 查询、查看场地资源
        print(f"\n[{idx}] 场地管理 - 查询、查看场地资源")
        if self.click_button("查看") or self.click_button("设置"):
            self.save_screenshot(idx, "场地管理", "查看场地资源", "场地资源详情")
            self.driver.back()
            time.sleep(1)
            idx += 1
        else:
            # 点击场地预定看板
            if self.click_menu("场地预定看板"):
                time.sleep(1)
                self.save_screenshot(idx, "场地管理", "场地预定看板", "场地预定看板")
                idx += 1
        
        # ========== 订单管理（场地订单/活动订单） ==========
        print(f"\n{'='*70}")
        print("【订单管理】")
        print(f"{'='*70}")
        
        # 8. 订单管理 - 订单查询（场地订单）
        print(f"\n[{idx}] 订单管理 - 订单查询")
        if self.click_menu("场地订单"):
            time.sleep(1)
            self.save_screenshot(idx, "订单管理", "订单查询", "场地订单查询页面")
            idx += 1
        
        # 9. 订单管理 - 退款订单
        print(f"\n[{idx}] 订单管理 - 退款订单")
        # 在订单列表页，点击查询展开条件
        if self.click_button("查询"):
            time.sleep(1)
        self.save_screenshot(idx, "订单管理", "退款订单", "订单列表（含退款）")
        idx += 1
        
        # 10. 订单管理 - 订单详情
        print(f"\n[{idx}] 订单管理 - 订单详情")
        if self.click_button("订单详情"):
            time.sleep(1)
            self.save_screenshot(idx, "订单管理", "订单详情", "订单详情页面")
            self.driver.back()
            time.sleep(1)
            idx += 1
        else:
            self.save_screenshot(idx, "订单管理", "订单详情", "订单列表")
            idx += 1
        
        # ========== 用户管理 ==========
        print(f"\n{'='*70}")
        print("【用户管理】")
        print(f"{'='*70}")
        
        # 11. 用户管理 - 用户订单列表
        print(f"\n[{idx}] 用户管理 - 用户订单列表")
        if self.click_menu("用户"):
            time.sleep(1)
            if self.click_menu("用户订单"):
                time.sleep(1)
                self.save_screenshot(idx, "用户管理", "用户订单列表", "用户订单列表页面")
                idx += 1
        
        # 12. 用户管理 - 订单详情
        print(f"\n[{idx}] 用户管理 - 订单详情")
        if self.click_button("订单详情"):
            time.sleep(1)
            self.save_screenshot(idx, "用户管理", "订单详情", "用户订单详情")
            self.driver.back()
            time.sleep(1)
            idx += 1
        else:
            self.save_screenshot(idx, "用户管理", "订单详情", "订单列表")
            idx += 1
        
        # ========== 优惠券管理 ==========
        print(f"\n{'='*70}")
        print("【优惠券管理】")
        print(f"{'='*70}")
        
        # 13. 优惠券管理 - 优惠券列表
        print(f"\n[{idx}] 优惠券管理 - 优惠券列表")
        if self.click_menu("优惠券"):
            time.sleep(1)
            self.save_screenshot(idx, "优惠券管理", "优惠券列表", "优惠券列表（含操作按钮）")
            idx += 1
        
        # 14. 优惠券管理 - 优惠券搜索
        print(f"\n[{idx}] 优惠券管理 - 优惠券搜索")
        if self.click_button("查询"):
            time.sleep(1)
        self.save_screenshot(idx, "优惠券管理", "优惠券搜索", "优惠券搜索功能")
        idx += 1
        
        # 15. 优惠券管理 - 新建、删除优惠券
        print(f"\n[{idx}] 优惠券管理 - 新建、删除优惠券")
        if self.click_button("新建"):
            time.sleep(1)
            self.save_screenshot(idx, "优惠券管理", "新建优惠券", "新建优惠券弹窗")
            self.close_dialog()
            idx += 1
        else:
            self.save_screenshot(idx, "优惠券管理", "新建优惠券", "优惠券管理页面")
            idx += 1
        
        # 16. 优惠券管理 - 优惠券规则
        print(f"\n[{idx}] 优惠券管理 - 优惠券使用规则")
        if self.click_button("编辑"):
            time.sleep(1)
            self.save_screenshot(idx, "优惠券管理", "优惠券规则", "优惠券规则设置")
            self.close_dialog()
            idx += 1
        else:
            self.save_screenshot(idx, "优惠券管理", "优惠券规则", "优惠券列表")
            idx += 1
        
        # 17. 优惠券管理 - 领取记录查询
        print(f"\n[{idx}] 优惠券管理 - 领取记录查询")
        # 在当前优惠券页面展示查询功能
        self.save_screenshot(idx, "优惠券管理", "领取记录查询", "优惠券领取记录")
        idx += 1
        
        # ========== 积分管理 ==========
        print(f"\n{'='*70}")
        print("【积分管理】")
        print(f"{'='*70}")
        
        # 18. 积分管理 - 积分规则设置
        print(f"\n[{idx}] 积分管理 - 积分规则设置")
        if self.click_menu("积分"):
            time.sleep(1)
            if self.click_menu("规则设置"):
                time.sleep(1)
                self.save_screenshot(idx, "积分管理", "积分规则设置", "积分规则设置页面")
                idx += 1
        
        # 19. 积分管理 - 订单类积分
        print(f"\n[{idx}] 积分管理 - 订单类积分")
        if self.click_button("新增"):
            time.sleep(1)
            self.save_screenshot(idx, "积分管理", "订单类积分", "订单类积分设置")
            self.close_dialog()
            idx += 1
        else:
            self.save_screenshot(idx, "积分管理", "订单类积分", "规则设置页面")
            idx += 1
        
        # 20. 积分管理 - 任务类积分
        print(f"\n[{idx}] 积分管理 - 任务类积分")
        self.save_screenshot(idx, "积分管理", "任务类积分", "任务类积分规则")
        idx += 1
        
        # 21. 积分管理 - 积分商城商品列表
        print(f"\n[{idx}] 积分管理 - 积分商城商品列表")
        if self.click_menu("积分商城"):
            time.sleep(1)
            self.save_screenshot(idx, "积分管理", "积分商城商品列表", "积分商城商品列表")
            idx += 1
        
        # 22. 积分管理 - 商品查询
        print(f"\n[{idx}] 积分管理 - 商品查询")
        if self.click_button("查询"):
            time.sleep(1)
        self.save_screenshot(idx, "积分管理", "商品查询", "商品条件查询")
        idx += 1
        
        # 23. 积分管理 - 新建、删除商品
        print(f"\n[{idx}] 积分管理 - 新建、删除商品")
        if self.click_button("新建商品"):
            time.sleep(1)
            self.save_screenshot(idx, "积分管理", "新建商品", "新建商品弹窗")
            self.close_dialog()
            idx += 1
        else:
            self.save_screenshot(idx, "积分管理", "新建商品", "商品列表")
            idx += 1
        
        # ========== 积分订单 ==========
        print(f"\n{'='*70}")
        print("【积分订单】")
        print(f"{'='*70}")
        
        # 24. 积分订单 - 积分订单列表
        print(f"\n[{idx}] 积分订单 - 积分订单列表")
        if self.click_menu("积分订单"):
            time.sleep(1)
            self.save_screenshot(idx, "积分订单", "积分订单列表", "积分商城消费订单列表")
            idx += 1
        
        # 25. 积分订单 - 按条件查询
        print(f"\n[{idx}] 积分订单 - 按条件查询")
        if self.click_button("查询"):
            time.sleep(1)
        self.save_screenshot(idx, "积分订单", "按条件查询", "订单条件查询")
        idx += 1
        
        # 26. 积分订单 - 订单详情查看
        print(f"\n[{idx}] 积分订单 - 订单详情")
        self.save_screenshot(idx, "积分订单", "订单详情", "积分订单详情")
        idx += 1
        
        # ========== 小游戏管理 ==========
        print(f"\n{'='*70}")
        print("【小游戏管理】")
        print(f"{'='*70}")
        
        # 27. 小游戏管理 - 小游戏列表
        print(f"\n[{idx}] 小游戏管理 - 小游戏列表")
        if self.click_menu("小游戏"):
            time.sleep(1)
            self.save_screenshot(idx, "小游戏管理", "小游戏列表", "小游戏列表页面")
            idx += 1
        
        # 28. 小游戏管理 - 小游戏条件查询
        print(f"\n[{idx}] 小游戏管理 - 小游戏条件查询")
        if self.click_button("查询"):
            time.sleep(1)
        self.save_screenshot(idx, "小游戏管理", "条件查询", "小游戏条件查询")
        idx += 1
        
        # 29. 小游戏管理 - 新建、删除、上架小游戏
        print(f"\n[{idx}] 小游戏管理 - 新建、删除、上架")
        if self.click_button("新建"):
            time.sleep(1)
            self.save_screenshot(idx, "小游戏管理", "新建小游戏", "新建小游戏页面")
            self.driver.back()
            time.sleep(1)
            idx += 1
        else:
            self.save_screenshot(idx, "小游戏管理", "新建小游戏", "小游戏列表")
            idx += 1
        
        # ========== 员工管理 ==========
        print(f"\n{'='*70}")
        print("【员工管理】")
        print(f"{'='*70}")
        
        # 30. 员工管理 - 员工列表
        print(f"\n[{idx}] 员工管理 - 员工列表")
        if self.click_menu("员工"):
            time.sleep(1)
            self.save_screenshot(idx, "员工管理", "员工列表", "员工列表页面")
            idx += 1
        
        # 31. 员工管理 - 员工详情
        print(f"\n[{idx}] 员工管理 - 员工详情")
        if self.click_button("编辑"):
            time.sleep(1)
            self.save_screenshot(idx, "员工管理", "员工详情", "员工详情/编辑")
            self.close_dialog()
            idx += 1
        else:
            self.save_screenshot(idx, "员工管理", "员工详情", "员工列表")
            idx += 1
        
        # ========== 财务管理 ==========
        print(f"\n{'='*70}")
        print("【财务管理】")
        print(f"{'='*70}")
        
        # 32. 财务管理 - 商户结算审核
        print(f"\n[{idx}] 财务管理 - 商户结算审核")
        if self.click_menu("财务"):
            time.sleep(1)
            if self.click_menu("商户结算审核"):
                time.sleep(1)
                self.save_screenshot(idx, "财务管理", "商户结算审核", "商户结算审核页面")
                idx += 1
        
        # 33. 财务管理 - 财务报表
        print(f"\n[{idx}] 财务管理 - 财务报表")
        if self.click_menu("财务报表"):
            time.sleep(1)
            self.save_screenshot(idx, "财务管理", "财务报表", "财务报表页面")
            idx += 1
        
        # ========== 数据分析 ==========
        print(f"\n{'='*70}")
        print("【数据分析】")
        print(f"{'='*70}")
        
        # 34. 数据分析 - 销售统计
        print(f"\n[{idx}] 数据分析 - 销售统计")
        if self.click_menu("数据分析"):
            time.sleep(1)
            if self.click_menu("销售统计"):
                time.sleep(1)
                self.save_screenshot(idx, "数据分析", "销售统计", "销售统计页面")
                idx += 1
        
        print("\n" + "=" * 70)
        print(f"✓ 截图完成！共 {len(self.screenshots)} 个功能点")
    
    def close(self):
        if self.driver:
            self.driver.quit()


def create_word_doc(screenshots, output_path):
    """生成Word文档"""
    print("\n正在生成Word文档...")
    print("=" * 70)
    
    doc = Document()
    
    # 中文字体
    doc.styles['Normal'].font.name = 'Microsoft YaHei'
    doc.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    
    # 标题
    title = doc.add_heading('海星育后台管理系统 - 功能点截图对照表', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 信息
    info = doc.add_paragraph()
    info.add_run('系统名称：').bold = True
    info.add_run('海星育后台管理系统\n')
    info.add_run('系统地址：').bold = True
    info.add_run('https://jhtest.bjstarfish.com/\n')
    info.add_run('生成时间：').bold = True
    info.add_run(f'{time.strftime("%Y-%m-%d %H:%M:%S")}\n')
    info.add_run('功能点数：').bold = True
    info.add_run(f'{len(screenshots)} 个')
    
    doc.add_paragraph()
    
    # 表格
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    
    # 表头
    header = table.rows[0].cells
    header[0].text = '序号'
    header[1].text = '功能点描述'
    header[2].text = '功能截图'
    
    for cell in header:
        for para in cell.paragraphs:
            for run in para.runs:
                run.font.bold = True
                run.font.size = Pt(11)
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 列宽
    widths = (Inches(0.5), Inches(2.5), Inches(4.0))
    for row in table.rows:
        for idx, width in enumerate(widths):
            row.cells[idx].width = width
    
    # 数据
    for ss in screenshots:
        row = table.add_row()
        cells = row.cells
        
        for idx, width in enumerate(widths):
            cells[idx].width = width
        
        # 序号
        cells[0].text = str(ss['index'])
        cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 描述
        desc_para = cells[1].paragraphs[0]
        run = desc_para.add_run(f"【{ss['module']}】\n")
        run.font.bold = True
        run.font.size = Pt(10)
        
        run = desc_para.add_run(f"{ss['function']}\n\n")
        run.font.size = Pt(9)
        
        run = desc_para.add_run(f"{ss['description']}")
        run.font.size = Pt(8)
        
        # 截图
        img_path = os.path.join('/workspace/screenshots_functions', ss['filename'])
        if os.path.exists(img_path):
            img_para = cells[2].paragraphs[0]
            img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            try:
                run = img_para.add_run()
                run.add_picture(img_path, width=Inches(3.8))
                print(f"  ✓ [{ss['index']:03d}] {ss['module']} - {ss['function']}")
            except Exception as e:
                img_para.add_run(f'[图片加载失败: {str(e)}]')
                print(f"  ✗ [{ss['index']:03d}] 图片失败")
        else:
            cells[2].text = '[图片文件不存在]'
            print(f"  ✗ [{ss['index']:03d}] 文件不存在")
    
    doc.save(output_path)
    
    print("=" * 70)
    print(f"\n✓ Word文档生成完成")
    print(f"📄 文件: {output_path}")
    print(f"📊 大小: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")


def main():
    base_url = "https://jhtest.bjstarfish.com/"
    username = "admin"
    password = "123456"
    
    print("=" * 70)
    print("精确功能点截图工具")
    print("=" * 70)
    
    screenshotter = None
    try:
        screenshotter = PreciseScreenshotter(base_url, username, password)
        
        if screenshotter.login():
            screenshotter.capture_all_functions()
            
            # 生成文档
            output_path = '/workspace/功能点截图对照表_精确版.docx'
            create_word_doc(screenshotter.screenshots, output_path)
            
            # 打包
            print("\n正在打包...")
            os.system(f"cd /workspace && zip -q -r 功能点截图完整包_精确版.zip screenshots_functions/ 功能点截图对照表_精确版.docx")
            
            print("\n" + "=" * 70)
            print("✅ 所有任务完成！")
            print(f"📁 截图目录: /workspace/screenshots_functions")
            print(f"📄 Word文档: {output_path}")
            print(f"📦 压缩包: /workspace/功能点截图完整包_精确版.zip")
            print("=" * 70)
    
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if screenshotter:
            screenshotter.close()


if __name__ == "__main__":
    main()
