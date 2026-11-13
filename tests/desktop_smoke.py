"""Optional browser-level smoke test using synthetic data; not a Tauri E2E test."""
import hashlib
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright
from reportlab.pdfgen import canvas

root = Path(os.environ["LPI_DESKTOP_ROOT"])
edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
output = Path(__file__).resolve().parents[1] / "docs" / "evidence" / "CTO-002-desktop-browser-smoke.png"
with tempfile.TemporaryDirectory(dir=root) as temp:
    source = Path(temp) / "synthetic.pdf"
    pdf = canvas.Canvas(str(source))
    pdf.drawString(72, 720, "Synthetic test page one")
    pdf.showPage()
    pdf.drawString(72, 720, "Synthetic test page two")
    pdf.showPage()
    pdf.save()
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    server = subprocess.Popen(["node", str(root / "node_modules/vite/bin/vite.js"), "--host", "127.0.0.1", "--port", "1420", "--strictPort"], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=edge, headless=True)
            page = browser.new_page(viewport={"width":1440,"height":900})
            page.route("**/*", lambda route: route.continue_() if route.request.url.startswith("http://127.0.0.1:1420/") else route.abort())
            for _ in range(100):
                try:
                    page.goto("http://127.0.0.1:1420/", wait_until="domcontentloaded", timeout=1000)
                    break
                except Exception:
                    if server.poll() is not None: raise RuntimeError("Vite exited before becoming ready")
                    time.sleep(.05)
            else: raise RuntimeError("Vite did not start")
            page.locator("input[type=file]").set_input_files(str(source))
            page.get_by_text("1 / 2", exact=True).wait_for(timeout=15000)
            page.wait_for_function("() => { const c=document.querySelector('canvas'); if (!c || c.width < 1) return false; const a=c.getContext('2d').getImageData(0,0,c.width,c.height).data; return a.some((v,i)=>i%4!==3 && v<100); }")
            first_page = page.locator("canvas").evaluate("c => c.toDataURL()")
            page.get_by_label("Tìm văn bản trong PDF").fill("page two")
            page.get_by_role("button", name="Tìm", exact=True).click()
            page.get_by_text("2 / 2", exact=True).wait_for(timeout=10000)
            page.wait_for_function("first => { const c=document.querySelector('canvas'); return c?.dataset.renderedPage === '2' && c.toDataURL() !== first; }", arg=first_page, timeout=15000)
            page.get_by_text("Tìm thấy tại trang 2", exact=True).wait_for(timeout=10000)
            page.get_by_label("Tìm văn bản trong PDF").fill("không tồn tại")
            page.get_by_role("button", name="Tìm", exact=True).click()
            page.get_by_text("Không tìm thấy văn bản trong tài liệu.", exact=True).wait_for(timeout=10000)
            page.screenshot(path=str(output))
            browser.close()
        assert hashlib.sha256(source.read_bytes()).hexdigest() == before
        print("PASS: browser viewer opened synthetic PDF, rendered page, found text on page 2, reported missing text; SHA-256 unchanged")
    finally:
        server.terminate()
        try: server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)
