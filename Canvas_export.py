import asyncio
import re
from pathlib import Path
from urllib.parse import urljoin
from lxml import html as LH
import pypandoc
from playwright.async_api import async_playwright

# Your course modules URL goes here.
COURSE_MODULES_URL = "https://canvas.lms.xxs"  #your url in canvas module, for example, https://canvas.lms.unimelb.edu.au/courses/YOUR_COURSE_ID/modules
# Remote debugging port address, typically 9222 for Chrome.
CDP_ENDPOINT = "http://127.0.0.1:9222"

# Output directories and file names
OUT_DIR = Path("canvas_export")
OUT_HTML = OUT_DIR / "course_merged.html"
OUT_DOCX = OUT_DIR / "course_merged.docx"

# CSS selectors for content extraction
CONTENT_SELECTORS = [
    "#wiki_page_show .show-content",
    "#content .show-content",
    "#content .user_content",
    ".ic-Layout-contentMain .user_content",
    "#assignment_show .description",
    "#assignment_show .user_content",
    ".quiz-index .user_content",
    ".discussion_topic .user_content",
    "#content", "main", "body"
]

# Patterns to identify files or external links
FILE_LIKE_PATTERNS = [
    "/files/", ".pdf", ".ppt", ".pptx", ".doc", ".docx", ".xls", ".xlsx",
    "/external_tools/", "/external_urls/"
]

async def safe_wait_networkidle(page, timeout_ms=4000):
    """
    Some pages may never reach networkidle; we wait a few seconds at most.
    """
    try:
        await page.wait_for_load_state("networkidle", timeout=timeout_ms)
    except Exception:
        pass

async def goto_settle(page, url, settle_ms=800):
    """
    Go to a URL, wait for DOMContentLoaded, then a short pause, and
    a non-blocking wait for networkidle.
    """
    await page.goto(url, wait_until="domcontentloaded", timeout=90000)
    await page.wait_for_timeout(settle_ms)
    await safe_wait_networkidle(page, 3000)

def sanitize(s: str) -> str:
    """Sanitize string for use in filenames."""
    s = s.strip()
    s = re.sub(r'[/\\:*?"<>|]+', "_", s)
    return s[:160] or "Untitled"

def looks_like_file_or_external(url: str) -> bool:
    """Check if a URL points to a file or an external link."""
    u = url.lower()
    return any(p in u for p in FILE_LIKE_PATTERNS)

async def auto_scroll(page, step=900, pause=250):
    """Scroll to the end of the page to load all content."""
    last = 0
    while True:
        height = await page.evaluate("document.scrollingElement.scrollHeight")
        if height <= last:
            break
        last = height
        await page.evaluate(f"window.scrollBy(0, {step});")
        await page.wait_for_timeout(pause)

async def expand_all_modules(page):
    """Click the 'Expand All' button to reveal all module items."""
    for sel in ["text=Expand All", "text=展开全部", "[data-testid='expand-all']",
                "button[aria-label*='Expand All' i]", "button:has-text('Expand All')"]:
        btn = await page.query_selector(sel)
        if btn:
            await btn.click()
            await page.wait_for_timeout(500)
            return

async def collect_module_item_links(page, base_url: str):
    """Collect unique links from the course modules page."""
    await page.wait_for_load_state("networkidle")
    await auto_scroll(page)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(400)
    items = await page.evaluate("""
    () => {
      const arr = [];
      document.querySelectorAll('a.ig-title, a[data-testid="context-module-item-title"], .ig-list a').forEach(a=>{
        const href = a.getAttribute('href') || '';
        const text = (a.textContent || '').trim();
        if(href) arr.push({href, text});
      });
      const seen = new Set();
      return arr.filter(x => {
        const k = x.href + '|' + x.text;
        if(seen.has(k)) return false;
        seen.add(k);
        return true;
      });
    }
    """)
    return [urljoin(base_url, it["href"]) for it in items if it.get("href")]

async def extract_content_from_page(page):
    """Extract the main content and title from a page."""
    title = (await page.title()) or ""
    try:
        h = await page.eval_on_selector("h1, .page-title, #breadcrumbs .ellipsible", "el => el.textContent", timeout=1500)
        if h and h.strip():
            title = h.strip()
    except:
        pass
    for sel in CONTENT_SELECTORS:
        try:
            await page.wait_for_selector(sel, timeout=1500)
            inner = await page.eval_on_selector(sel, "el => el.innerHTML")
            if inner and inner.strip():
                return sanitize(title), inner
        except:
            continue
    html_full = await page.content()
    try:
        tree = LH.fromstring(html_full)
        body = tree.xpath("//body")
        if body:
            return sanitize(title or "Untitled"), LH.tostring(body[0], encoding="unicode")
    except:
        pass
    return sanitize(title or "Untitled"), ""

def build_combined_html(base_href: str, sections: list[str]) -> str:
    """Build a single HTML file from all scraped sections."""
    css = """
    body{font-family:Arial,"Microsoft Yahei",sans-serif;line-height:1.55;}
    h1,h2,h3{page-break-after:avoid;}
    img,table{max-width:100%;}
    .page-sep{page-break-before:always;}
    .file-note{padding:8px 10px;border-left:4px solid #ccc;background:#f7f7f7;margin:8px 0;}
    """
    parts = [
        "<!doctype html>",
        "<html><head><meta charset='utf-8'>",
        f"<base href='{base_href}'>",
        f"<style>{css}</style>",
        "</head><body>"
    ]
    parts.extend(sections)
    parts.append("</body></html>")
    return "\n".join(parts)

async def main():
    """Main function to run the scraping process."""
    OUT_DIR.mkdir(exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_ENDPOINT)
        ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        await goto_settle(page, COURSE_MODULES_URL)
        await expand_all_modules(page)

        links = await collect_module_item_links(page, COURSE_MODULES_URL)
        print(f"Found {len(links)} module items.")

        sections = []
        for i, url in enumerate(links, 1):
            if looks_like_file_or_external(url):
                title = url.split("/")[-1]
                html = f"""
                    <h1>{sanitize(title)}</h1>
                    <div class="file-note">File/External Link, click to access:</div>
                    <p><a href="{url}">{url}</a></p>
                    <div class="page-sep"></div>
                """
                sections.append(html)
                print(f"[{i}] File/External Link: {title}")
                continue
            
            await goto_settle(page, url)
            
            title, inner = await extract_content_from_page(page)
            if not inner.strip():
                html = f"""
                    <h1>{title}</h1>
                    <div class="file-note">Failed to capture content, click to access:</div>
                    <p><a href="{url}">{url}</a></p>
                    <div class="page-sep"></div>
                """
            else:
                html = f"<h1>{title}</h1>\n{inner}\n<div class='page-sep'></div>"
            sections.append(html)
            print(f"[{i}] OK: {title}")

        combined_html = build_combined_html(COURSE_MODULES_URL, sections)
        OUT_HTML.write_text(combined_html, encoding="utf-8")
        print(f"\nGenerated HTML file: {OUT_HTML.resolve()}")

        try:
            pypandoc.convert_file(str(OUT_HTML), "docx", outputfile=str(OUT_DOCX))
            print(f"✅ Generated Word file: {OUT_DOCX.resolve()}")
        except OSError:
            print("❗ Pandoc not detected. Please install: https://pandoc.org/installing.html")

if __name__ == "__main__":
    asyncio.run(main())
