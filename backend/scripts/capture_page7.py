import os
import time
from playwright.sync_api import sync_playwright

def capture():
    html_path = os.path.abspath("../frontend/visit_completed.html")
    file_url = f"file:///{html_path.replace(os.sep, '/')}"
    output_path = os.path.abspath("../frontend/visit_completed_preview.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(
            viewport={"width": 1536, "height": 1024},
            device_scale_factor=1
        )
        page = context.new_page()
        page.goto(file_url, wait_until="networkidle")
        time.sleep(1.0)
        page.screenshot(path=output_path, full_page=False)
        browser.close()
        print(f"Captured screenshot to: {output_path}")

if __name__ == "__main__":
    capture()
