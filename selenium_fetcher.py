import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time


def render_notifications_page(login_url, notifications_url, username=None, password=None, timeout=15):
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    try:
        driver.set_page_load_timeout(timeout)
        if username and password:
            driver.get(login_url)
            time.sleep(1)
            # try common selectors
            user = None
            try:
                user = driver.find_element(By.NAME, 'username')
            except Exception:
                try:
                    user = driver.find_element(By.NAME, 'email')
                except Exception:
                    pass
            pwd = None
            try:
                pwd = driver.find_element(By.NAME, 'password')
            except Exception:
                pass
            if user:
                user.clear(); user.send_keys(username)
            if pwd:
                pwd.clear(); pwd.send_keys(password)
            # submit
            try:
                btn = driver.find_element(By.XPATH, "//button[@type='submit']")
                btn.click()
            except Exception:
                try:
                    pwd.send_keys(Keys.ENTER)
                except Exception:
                    pass
            time.sleep(2)
        driver.get(notifications_url)
        time.sleep(2)
        html = driver.page_source
        return html
    finally:
        try:
            driver.quit()
        except Exception:
            pass
