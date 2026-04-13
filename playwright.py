#使用playwright自动登录

from playwright.sync_api import sync_playwright 
if __name__=='__main__':
    User=''
    Password=''
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('')
        page.fill('input[id="username"]', User)
        page.fill('input[id="password"]', Password)
        page.click('button[id="login-account"]')
        page.wait_for_load_state('networkidle')
        print("Login successful!")
        browser.close()