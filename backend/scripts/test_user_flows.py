import os
from playwright.sync_api import sync_playwright

frontend_dir = os.path.abspath("../frontend").replace(os.sep, "/")

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    context = browser.new_context(viewport={"width": 1536, "height": 1024})
    page = context.new_page()

    # 1. Test Login Form
    print("Testing Login flow...")
    page.goto(f"file:///{frontend_dir}/login.html")
    page.click("#demo-fill-btn")
    page.click("#submit-btn")
    page.wait_for_timeout(1200)
    print(f"After login submit URL: {os.path.basename(page.url)}")
    assert page.url.endswith("home.html")

    # 2. Test Navigation: Home -> Seats
    print("Testing Home -> Seats...")
    page.click("a[href='seats.html']")
    page.wait_for_timeout(500)
    print(f"URL: {os.path.basename(page.url)}")
    assert page.url.endswith("seats.html")

    # 3. Test Navigation: Seats -> Menu
    print("Testing Seats -> Menu...")
    page.click("a[href='menu.html']")
    page.wait_for_timeout(500)
    print(f"URL: {os.path.basename(page.url)}")
    assert page.url.endswith("menu.html")

    # 4. Test Navigation: Menu -> Settings
    print("Testing Menu -> Settings...")
    page.click("a[href='settings.html']")
    page.wait_for_timeout(500)
    print(f"URL: {os.path.basename(page.url)}")
    assert page.url.endswith("settings.html")

    # 5. Test Navigation: Settings -> Notifications
    print("Testing Settings -> Notifications...")
    page.click("a[href='notifications.html']")
    page.wait_for_timeout(500)
    print(f"URL: {os.path.basename(page.url)}")
    assert page.url.endswith("notifications.html")

    # 6. Test Navigation: Notifications -> Visit History
    print("Testing Notifications -> Visit History...")
    page.click("a[href='visit_history.html']")
    page.wait_for_timeout(500)
    print(f"URL: {os.path.basename(page.url)}")
    assert page.url.endswith("visit_history.html")

    # 7. Test Navigation: Visit History -> Home
    print("Testing Visit History -> Home...")
    page.click("a[href='home.html']")
    page.wait_for_timeout(500)
    print(f"URL: {os.path.basename(page.url)}")
    assert page.url.endswith("home.html")

    # 8. Test Entry Scan -> Entry Success
    print("Testing Entry Scan -> Entry Success...")
    page.goto(f"file:///{frontend_dir}/entry_scan.html")
    page.click("#scanner-interactive-card")
    page.wait_for_timeout(1400)
    print(f"After scan URL: {os.path.basename(page.url)}")
    assert page.url.endswith("entry_success.html")

    # 9. Test Tray Return -> Visit Completed
    print("Testing Tray Return -> Visit Completed...")
    page.goto(f"file:///{frontend_dir}/tray_return.html")
    page.click("#scanner-interactive-card")
    page.wait_for_timeout(1400)
    print(f"After tray return URL: {os.path.basename(page.url)}")
    assert page.url.endswith("visit_completed.html")

    browser.close()
    print("\nALL USER FLOWS AND CROSS-PAGE NAVIGATION PASSED PERFECTLY!")
