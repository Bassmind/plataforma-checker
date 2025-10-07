import os
from playwright.sync_api import sync_playwright


def render_notifications_page(login_url, notifications_url, username=None, password=None, timeout=15000):
    """Open a headless browser, optionally login, navigate to notifications_url and return page HTML."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        # navigate to login first if credentials provided
        if username and password:
            page.goto(login_url, timeout=timeout)
            # try to fill common fields
            try:
                # detect input names
                if page.query_selector('input[name="username"]'):
                    page.fill('input[name="username"]', username)
                elif page.query_selector('input[name="email"]'):
                    page.fill('input[name="email"]', username)
                if page.query_selector('input[type="password"]'):
                    page.fill('input[type="password"]', password)
                # submit form
                if page.query_selector('button[type="submit"]'):
                    page.click('button[type="submit"]')
                else:
                    page.keyboard.press('Enter')
                page.wait_for_load_state('networkidle', timeout=timeout)
            except Exception:
                pass

        page.goto(notifications_url, timeout=timeout)
        page.wait_for_load_state('networkidle', timeout=timeout)
        html = page.content()
        try:
            context.close()
            browser.close()
        except Exception:
            pass
        return html
