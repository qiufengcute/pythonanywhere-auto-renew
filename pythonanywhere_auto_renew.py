"""
PythonAnywhere 自动续期脚本
使用浏览器自动化
"""

import os
import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

def renew_via_browser(username, password):
    print("使用浏览器自动化方式...")
    
    with sync_playwright() as p:
        # 在GitHub Actions中必须使用headless模式
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--no-first-run',
                '--disable-default-apps',
                '--disable-extensions',
                '--mute-audio'
            ]
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        try:
            # 步骤1: 直接导航到webapps页面
            print("步骤1: 导航到Web应用页面...")
            webapp_url = f"https://www.pythonanywhere.com/user/{username}/webapps/#id_{username.lower()}_pythonanywhere_com"

            print(f"正在访问: {webapp_url}")
            try:
                # 先尝试短超时快速检测
                page.goto(webapp_url, timeout=15000)
                print("✓ 页面导航成功")
            except Exception as e:
                print(f"页面导航失败（15秒超时）: {e}")
                print("重试导航，使用更长超时时间...")
                page.goto(webapp_url, timeout=60000)
                print("✓ 页面导航成功（重试）")

            # 等待页面开始加载
            page.wait_for_load_state('domcontentloaded', timeout=30000)

            # 多次检查URL变化（处理重定向）
            max_checks = 10
            for i in range(max_checks):
                current_url = page.url
                if "login" in current_url:
                    print("✓ 检测到登录页面，开始自动登录...")
                    break
                elif "user" in current_url and "webapps" in current_url:
                    print("✓ 已在Web应用页面，无需登录")
                    break
                else:
                    page.wait_for_timeout(2000)

            # 最终检查是否需要登录
            current_url = page.url
            if "login" in current_url:
                print("开始登录流程...")

                # 确保登录页面完全加载
                page.wait_for_load_state('networkidle', timeout=30000)

                # 步骤2: 填写登录信息
                print("步骤2: 填写登录信息...")
                username_input = page.wait_for_selector("input[name='auth-username']", timeout=20000)
                username_input.fill(username)
                print("✓ 用户名已填写")

                password_input = page.wait_for_selector("input[name='auth-password']", timeout=20000)
                password_input.fill(password)
                print("✓ 密码已填写")

                # 步骤3: 点击登录按钮
                print("步骤3: 点击登录按钮...")
                login_button = page.wait_for_selector("button[type='submit']", timeout=20000)
                login_button.click()
                print("✓ 登录按钮已点击")

                # 步骤4: 等待登录成功 - 使用多种等待策略
                print("步骤4: 等待登录完成...")
                login_success = False

                # 策略1: 等待URL变化
                try:
                    page.wait_for_url("**/user/**", timeout=45000)
                    print("✓ 通过URL变化检测到登录成功")
                    login_success = True
                except Exception as e:
                    print(f"URL等待超时: {e}")

                # 策略2: 检查页面内容变化
                if not login_success:
                    try:
                        page.wait_for_selector("input[name='auth-username']", state="hidden", timeout=10000)
                        print("✓ 通过页面内容变化检测到登录成功")
                        login_success = True
                    except Exception as e:
                        print(f"页面内容检测失败: {e}")

                # 策略3: 检查是否有用户菜单
                if not login_success:
                    try:
                        page.wait_for_selector("a[href*='dashboard']", timeout=10000)
                        print("✓ 检测到用户界面，登录成功")
                        login_success = True
                    except Exception as e:
                        print(f"用户界面检测失败: {e}")

                if login_success:
                    print("✓ 登录成功！")
                else:
                    raise Exception("所有登录检测方法都失败")

                # 重新导航到webapp页面
                print("重新导航到Web应用页面...")
                page.goto(webapp_url, timeout=60000)
                page.wait_for_load_state('networkidle', timeout=30000)

            # 步骤5: 等待webapp页面完全加载
            print("步骤5: 等待Web应用页面完全加载...")
            page.wait_for_load_state('domcontentloaded', timeout=30000)
            page.wait_for_load_state('networkidle', timeout=30000)

            # 额外等待确保动态内容加载完成
            page.wait_for_timeout(8000)

            # 验证页面是否正确加载
            current_url = page.url
            if "webapps" not in current_url:
                raise Exception(f"页面URL不正确: {current_url}")

            print("✓ Web应用页面加载完成")
            
            # 步骤6: 查找续期按钮 - 使用多种方法
            print("步骤6: 查找续期按钮...")

            renew_button = None

            # 方法1: 使用精确的CSS选择器（最优先）
            try:
                css_selector = "input[type='submit'][class='btn btn-warning webapp_extend'][value='Run until 1 month from today']"
                renew_button = page.wait_for_selector(css_selector, timeout=10000)
                if renew_button:
                    print("✓ 使用精确CSS选择器找到续期按钮")
                    try:
                        tag_name = renew_button.evaluate("el => el.tagName.toLowerCase()")
                        input_type = renew_button.get_attribute("type")
                        input_value = renew_button.get_attribute("value")
                        input_class = renew_button.get_attribute("class")
                        print(f"元素信息: {tag_name} type='{input_type}' value='{input_value}' class='{input_class}'")
                    except Exception as e:
                        print(f"获取元素信息失败: {e}")
            except Exception as e:
                print(f"精确CSS选择器失败: {e}")

            # 方法2: 通过value属性查找
            if not renew_button:
                try:
                    renew_button = page.wait_for_selector("input[value='Run until 1 month from today']", timeout=5000)
                    if renew_button:
                        print("✓ 通过value属性找到续期按钮")
                except Exception as e:
                    print(f"value属性查找失败: {e}")

            # 方法3: 通过class查找
            if not renew_button:
                try:
                    renew_button = page.wait_for_selector("input.webapp_extend", timeout=5000)
                    if renew_button:
                        print("✓ 通过class找到续期按钮")
                except Exception as e:
                    print(f"class查找失败: {e}")

            # 方法4: 遍历所有input元素查找
            if not renew_button:
                try:
                    all_inputs = page.query_selector_all("input[type='submit']")
                    for input_elem in all_inputs:
                        try:
                            value = input_elem.get_attribute("value") or ""
                            if "Run until" in value and "months" in value:
                                renew_button = input_elem
                                print(f"✓ 通过遍历找到续期按钮: {value}")
                                break
                        except:
                            continue
                except Exception as e:
                    print(f"遍历查找失败: {e}")

            if not renew_button:
                return False, "使用所有方法都未找到续期按钮"

            # 步骤7: 点击续期按钮
            print("步骤7: 点击续期按钮...")
            try:
                renew_button.scroll_into_view_if_needed()
                page.wait_for_timeout(2000)

                # 确保按钮可见和可点击
                is_visible = renew_button.is_visible()
                is_enabled = renew_button.is_enabled()
                print(f"按钮状态 - 可见: {is_visible}, 可点击: {is_enabled}")

                if is_visible and is_enabled:
                    renew_button.click()
                    print("✓ 续期按钮已点击")
                else:
                    raise Exception("按钮不可点击")

            except Exception as e:
                return False, f"点击按钮失败: {e}"

            # 步骤8: 等待续期操作完成
            print("步骤8: 等待续期操作完成...")
            page.wait_for_timeout(5000)

            try:
                page.wait_for_load_state('networkidle', timeout=15000)
                print("✓ 续期操作完成，页面已更新")
            except Exception as e:
                print(f"等待页面更新超时，但操作可能已成功: {e}")

            print("✓ 续期操作完成")

            # 获取到期日期
            expiry_date = "未知"
            try:
                date_elements = page.locator("text=/This site will be disabled on/").all_text_contents()
                if date_elements:
                    expiry_date = date_elements[0].replace('This site will be disabled on', '').strip()
                print(f"续期后到期日期: {expiry_date}")
            except:
                print("无法获取到期日期")

            browser.close()
            return True, f"续期成功！网站已延长到: {expiry_date}"
            
        except Exception as e:
            browser.close()
            return False, f"浏览器自动化失败: {str(e)}"


def main():
    print("DEBUG: main() 函数开始执行")
    username = os.getenv("PYTHONANYWHERE_USERNAME")
    password = os.getenv("PYTHONANYWHERE_PASSWORD")

    print(f"DEBUG: 用户名 = {username}")
    print(f"DEBUG: 密码 = {'*' * len(password) if password else 'None'}")

    if not username or not password:
        print("错误: 请设置环境变量 PYTHONANYWHERE_USERNAME 和 PYTHONANYWHERE_PASSWORD")
        sys.exit(1)
    
    webapp_id = f"{username}_pythonanywhere_com"
    
    print("=" * 60)
    print("PythonAnywhere 自动续期脚本")
    print("=" * 60)
    print(f"用户名: {username}")
    print(f"Web应用ID: {webapp_id}\n")
    
    # 直接使用浏览器自动化
    print("[浏览器自动化] 开始续期流程...")
    success, message = renew_via_browser(username, password)
    
    print("\n" + "=" * 60)
    if success:
        print(f"✓ {message}")
    else:
        print(f"✗ {message}")
    print("=" * 60)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
