# 自动化网站截图工具

这个工具可以自动访问指定网站，登录后遍历所有页面并截图。

## 功能特性

- ✅ 自动登录网站
- ✅ 智能发现和遍历所有页面链接
- ✅ 自动截图每个页面
- ✅ 生成详细的截图报告（JSON 和 Markdown 格式）
- ✅ 支持无头模式运行
- ✅ 自动处理动态加载内容

## 安装依赖

```bash
pip install -r requirements_screenshotter.txt
```

注意：您还需要安装 Chrome 浏览器和 ChromeDriver。

### 在 Linux 上安装 Chrome 和 ChromeDriver

```bash
# 安装 Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb

# 安装 ChromeDriver
sudo apt-get install -y chromium-chromedriver
```

## 使用方法

### 基本使用

```bash
python website_screenshotter.py
```

### 自定义配置

编辑 `website_screenshotter.py` 文件中的 `main()` 函数：

```python
def main():
    base_url = "https://jhtest.bjstarfish.com/"  # 目标网站
    username = "admin"                            # 用户名
    password = "123456"                           # 密码
    output_dir = "screenshots"                    # 输出目录
    max_pages = 50                                # 最多截图页面数
    ...
```

## 输出文件

运行后会在 `screenshots` 目录下生成：

- `00_login_page.png` - 登录页面截图
- `01_after_login.png` - 登录后页面截图
- `002_xxx.png`, `003_xxx.png`, ... - 各个页面的截图
- `report.json` - JSON 格式的详细报告
- `report.md` - Markdown 格式的图文报告

## 工作流程

1. 访问目标网站
2. 自动填写用户名和密码并登录
3. 从首页开始，递归发现所有链接
4. 访问每个链接并截图
5. 生成详细报告

## 注意事项

- 工具使用无头浏览器运行，不会显示浏览器窗口
- 默认截图分辨率为 1920x1080
- 只会截取同域名下的页面
- 会自动去重，避免重复访问同一页面

## 故障排除

如果遇到问题：

1. 确保已安装 Chrome 浏览器和 ChromeDriver
2. 检查网络连接是否正常
3. 查看错误截图（如果生成）
4. 检查目标网站是否需要特殊的登录流程

## 许可证

MIT License
