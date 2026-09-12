import os
from playwright.sync_api import sync_playwright

PAGES = [
    "login.html",
    "home.html",
    "entry_scan.html",
    "entry_success.html",
    "my_visit.html",
    "tray_return.html",
    "visit_completed.html",
    "visit_history.html",
    "notifications.html",
    "seats.html",
    "menu.html",
    "settings.html"
]

def test_pages():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        
        for page_name in PAGES:
            html_path = os.path.abspath(f"../frontend/{page_name}")
            file_url = f"file:///{html_path.replace(os.sep, '/')}"
            
            context = browser.new_context(
                viewport={"width": 1536, "height": 1024},
                device_scale_factor=1
            )
            # Add mock token so pages that require auth don't kick to login
            context.add_init_script("""
                localStorage.setItem('dinespace_jwt_token', 'mock_token_123');
                localStorage.setItem('dinespace_token', 'mock_token_123');
                localStorage.setItem('dinespace_user_info', JSON.stringify({
                    studentId: 'P132-NNK',
                    fullName: 'Kunal Kumar Singh',
                    department: 'CSE'
                }));
            """)
            
            page = context.new_page()
            console_errors = []
            page_errors = []
            
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda err: page_errors.append(str(err)))
            
            try:
                page.goto(file_url, wait_until="networkidle", timeout=10000)
                final_url = page.url
                redirected = not final_url.endswith(page_name)
                print(f"[{page_name}] Final URL: {os.path.basename(final_url)} | Redirected: {redirected}")
                if console_errors:
                    print(f"  Console Errors ({len(console_errors)}): {console_errors}")
                if page_errors:
                    print(f"  Page JS Errors ({len(page_errors)}): {page_errors}")
                
                if page_name in ["seats.html", "menu.html", "settings.html"]:
                    img_path = os.path.abspath(f"../frontend/{page_name.replace('.html', '_preview.png')}")
                    page.screenshot(path=img_path, full_page=True)
                    print(f"  Captured screenshot: {os.path.basename(img_path)}")
            except Exception as e:
                print(f"[{page_name}] Exception during load: {e}")
            finally:
                context.close()
                
        browser.close()

if __name__ == "__main__":
    test_pages()
