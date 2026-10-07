import io
import re
import requests
from bs4 import BeautifulSoup

# Import pdfplumber and PyPDF2/pypdf with fallback checks
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    try:
        import pypdf as PyPDF2
        PYPDF2_AVAILABLE = True
    except ImportError:
        PYPDF2_AVAILABLE = False


import unicodedata


def looks_garbled(text: str) -> bool:
    """Detect text from legacy (non-Unicode) Indic fonts, e.g. SakalMarathi.

    Two symptoms: pdfplumber emits '(cid:123)' for unmapped glyphs, and
    pypdf emits Latin-Extended symbols (Ģ, Ď, ¾, Ǐ...) in place of Devanagari.
    Either way, vowel signs are also out of order, so OCR is the safe fix.
    """
    if not text:
        return False
    if len(re.findall(r"\(cid:\d+\)", text)) >= 10:
        return True
    odd = len(re.findall(r"[\u00A1-\u024F\u0370-\u03FF]", text))
    deva = len(re.findall(r"[\u0900-\u097F]", text))
    return odd > 0.03 * len(text) and odd > deva * 0.2


def _render_pages(pdf_bytes: bytes, dpi: int = 300):
    """Render PDF pages to PIL images. PyMuPDF first (pip-only), poppler as fallback."""
    try:
        import fitz  # PyMuPDF
        from PIL import Image
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        return [Image.open(io.BytesIO(p.get_pixmap(dpi=dpi).tobytes("png"))) for p in doc]
    except ImportError:
        from pdf2image import convert_from_bytes  # needs poppler on PATH
        return convert_from_bytes(pdf_bytes, dpi=dpi)


def ocr_pdf(pdf_bytes: bytes, lang: str = "mar+eng", dpi: int = 300) -> str:
    """OCR fallback for legacy-font / scanned PDFs.

    Needs: pip install pymupdf pytesseract pillow
    plus the Tesseract program with the Marathi language data (mar.traineddata).
    """
    import os
    try:
        import pytesseract
    except ImportError as e:
        raise ValueError("OCR needs: pip install pymupdf pytesseract pillow") from e

    # Windows: default install location is often not on PATH
    win_exe = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.name == "nt" and os.path.exists(win_exe):
        pytesseract.pytesseract.tesseract_cmd = win_exe

    try:
        installed = pytesseract.get_languages(config="")
    except Exception as e:
        raise ValueError(
            "Tesseract is not installed. Windows: install from "
            "https://github.com/UB-Mannheim/tesseract/wiki (tick 'Marathi' under "
            "Additional language data)."
        ) from e
    if "mar" not in installed:
        raise ValueError(
            "Tesseract is missing Marathi data. Download mar.traineddata from "
            "https://github.com/tesseract-ocr/tessdata_fast and put it in "
            "C:\\Program Files\\Tesseract-OCR\\tessdata, then retry."
        )

    pages = _render_pages(pdf_bytes, dpi)
    return "\n\n".join(pytesseract.image_to_string(p, lang=lang) for p in pages)


def normalize_text(text: str) -> str:
    """NFC-normalize, strip PDF junk (signature block, page footers, hyphen breaks)."""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"Digitally signed by.*?(?=\n\S*\s*\n|$)", "", text, flags=re.S)
    text = re.sub(r"पृष्ठ\s*\d+\s*पैकी\s*\d+", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text_from_pdf(pdf_file) -> str:
    """
    Extracts text from a PDF file (UploadedFile object or BytesIO).
    Uses pdfplumber as primary extractor, with PyPDF2/pypdf as fallback.
    """
    if pdf_file is None:
        raise ValueError("No PDF file provided.")

    # Read bytes from file object
    if hasattr(pdf_file, "read"):
        pdf_bytes = pdf_file.read()
        if hasattr(pdf_file, "seek"):
            pdf_file.seek(0)
    elif isinstance(pdf_file, bytes):
        pdf_bytes = pdf_file
    else:
        raise ValueError("Invalid PDF file type.")

    extracted_text = ""

    # Attempt 1: pdfplumber
    if PDFPLUMBER_AVAILABLE:
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                pages_text = []
                for page in pdf.pages:
                    page_t = page.extract_text()
                    if page_t:
                        pages_text.append(page_t)
                if pages_text:
                    extracted_text = "\n\n".join(pages_text)
        except Exception:
            extracted_text = ""

    # Attempt 2: Fallback to PyPDF2 / pypdf
    if not extracted_text.strip() and PYPDF2_AVAILABLE:
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            pages_text = []
            for page in reader.pages:
                page_t = page.extract_text()
                if page_t:
                    pages_text.append(page_t)
            if pages_text:
                extracted_text = "\n\n".join(pages_text)
        except Exception:
            pass

    extracted_text = extracted_text.strip()

    # Legacy-font PDFs give mojibake -> re-read the pages with OCR instead.
    if extracted_text and looks_garbled(extracted_text):
        extracted_text = ocr_pdf(pdf_bytes).strip()
    elif not extracted_text:
        try:
            extracted_text = ocr_pdf(pdf_bytes).strip()
        except ValueError:
            pass

    extracted_text = normalize_text(extracted_text) if extracted_text else ""
    if not extracted_text:
        raise ValueError("Failed to extract selectable text from PDF. The document might be scanned, image-only, or password protected.")

    return extracted_text


def is_listing_or_search_page(soup: BeautifulSoup, url: str, text: str) -> bool:
    """
    Detects if the scraped webpage is a search/listing/directory page rather than
    a detailed individual government scheme page.
    """
    url_lower = url.lower()
    text_lower = text.lower()
    
    # URL pattern indicators
    if re.search(r'/(?:search|schemes-list|all-schemes|category|directory|browse)\b', url_lower):
        return True
        
    # Page Title indicators
    title_tag = soup.find('title')
    title_text = title_tag.get_text().lower() if title_tag else ""
    if any(phrase in title_text for phrase in [
        "search schemes", "find schemes", "scheme directory", "all schemes", "list of schemes", "browse schemes"
    ]):
        return True

    # Main Heading indicators
    h1_tag = soup.find('h1')
    h1_text = h1_tag.get_text().lower() if h1_tag else ""
    if any(phrase in h1_text for phrase in [
        "search schemes", "find schemes", "scheme directory", "all schemes", "list of schemes", "filter schemes"
    ]):
        return True

    # Text content indicators (high link count with listing keywords and lack of scheme detail sections)
    listing_phrases = ["search schemes", "select state", "filter by category", "total schemes found", "showing schemes"]
    listing_matches = sum(1 for p in listing_phrases if p in text_lower)
    
    detail_phrases = ["eligibility criteria", "application procedure", "required documents", "key benefits", "how to apply"]
    detail_matches = sum(1 for p in detail_phrases if p in text_lower)

    if listing_matches >= 2 and detail_matches == 0:
        return True

    return False


_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
MIN_STATIC_CHARS = 400  # shorter than this usually means a JavaScript-rendered shell


def _normalize_url(url: str) -> str:
    if not url or not isinstance(url, str):
        raise ValueError("Invalid or empty URL provided.")
    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url
    return url


def _fetch_static_html(url: str) -> bytes:
    headers = {
        "User-Agent": _UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
    }
    response = None
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.content
    except requests.exceptions.MissingSchema:
        raise ValueError(f"Invalid URL format: '{url}'. Please include http:// or https://")
    except requests.exceptions.InvalidURL:
        raise ValueError(f"The URL '{url}' is invalid.")
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"HTTP error occurred while fetching URL (Status {response.status_code}): {e}")
    except requests.exceptions.ConnectionError:
        raise ValueError(f"Could not connect to target host '{url}'. Please check the URL or domain name.")
    except requests.exceptions.Timeout:
        raise ValueError(f"Request to '{url}' timed out (exceeded 15 seconds).")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch content from URL: {str(e)}")


def _launch_browser(p):
    """Try, in order: system Chromium (Linux/Streamlit Cloud), installed Chrome/Edge
    (Windows/Mac), Playwright's own Chromium, then download it once and retry."""
    import os, shutil, subprocess, sys
    args = ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
    attempts = []
    for exe in ("/usr/bin/chromium", "/usr/bin/chromium-browser", shutil.which("chromium")):
        if exe and os.path.exists(exe):
            attempts.append({"executable_path": exe})
    attempts += [{"channel": "chrome"}, {"channel": "msedge"}, {}]

    last = None
    for kw in attempts:
        try:
            return p.chromium.launch(headless=True, args=args, **kw)
        except Exception as e:  # noqa: BLE001
            last = e
    try:  # one-time download of Playwright's Chromium
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"],
                       check=True, capture_output=True, timeout=300)
        return p.chromium.launch(headless=True, args=args)
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"No usable browser found ({last}; install attempt: {e})")


def _render_html_playwright(url: str, timeout_ms: int = 45000) -> str:
    """Load the page in headless Chromium so JavaScript runs, return final HTML."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise RuntimeError("Playwright is not installed (pip install playwright).") from e

    def _work():
        with sync_playwright() as p:
            browser = _launch_browser(p)
            try:
                ctx = browser.new_context(user_agent=_UA, locale="en-IN",
                                          viewport={"width": 1366, "height": 900})
                page = ctx.new_page()
                # skip images/fonts/media: faster and not needed for text
                page.route("**/*", lambda r: r.abort()
                           if r.request.resource_type in ("image", "media", "font") else r.continue_())
                page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                try:  # wait until the app has actually rendered a decent amount of text
                    page.wait_for_function(
                        "document.body && document.body.innerText.length > 800",
                        timeout=20000)
                except Exception:  # noqa: BLE001
                    pass
                page.wait_for_timeout(1500)
                return page.content()
            finally:
                browser.close()

    # Run in a worker thread: avoids clashes with Streamlit's / Jupyter's event loop
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(_work).result(timeout=120)


def _html_to_text(html, url: str) -> str:
    try:
        soup = BeautifulSoup(html, "html.parser")

        # Decompose script, style, noscript, svg, iframe
        for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
            tag.decompose()

        # Check for listing/search page
        page_raw_text = soup.get_text(separator=" ")
        if is_listing_or_search_page(soup, url, page_raw_text):
            raise ValueError("This URL appears to be a scheme listing/search page. Please provide an individual scheme page URL.")

        # Extract structured content from headings, paragraphs, lists, tables, and main sections
        extracted_blocks = []

        # Target main content container if available
        main_container = (
            soup.find("main")
            or soup.find("article")
            or soup.find(id=re.compile(r"content|main|article|scheme", re.I))
            or soup.find(class_=re.compile(r"content|main|article|scheme", re.I))
            or soup.body
            or soup
        )

        # Iterate over key semantic tags in document order
        for element in main_container.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "ul", "ol", "tr", "div"]):
            # Ignore nested elements if parent is already processed, or extract clean text
            if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                txt = element.get_text(strip=True)
                if txt and len(txt) > 2:
                    extracted_blocks.append(f"\n{txt.upper()}:")
            elif element.name in ["p", "tr"]:
                txt = element.get_text(separator=" ", strip=True)
                if txt and len(txt) > 5:
                    extracted_blocks.append(txt)
            elif element.name in ["ul", "ol"]:
                items = [li.get_text(strip=True) for li in element.find_all("li") if li.get_text(strip=True)]
                if items:
                    extracted_blocks.append("\n".join(f"- {it}" for it in items))
            elif element.name == "div" and not element.find_all(["p", "ul", "ol", "div"]):
                txt = element.get_text(strip=True)
                if txt and len(txt) > 15:
                    extracted_blocks.append(txt)

        # Fallback to direct text if block extraction yielded very few blocks
        if len(extracted_blocks) < 3:
            raw_text = main_container.get_text(separator="\n")
            lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
            extracted_blocks = lines

        # Clean & join
        clean_text = "\n".join(extracted_blocks).strip()

        if len(clean_text) < 15:
            raise ValueError("Could not extract readable text from the specified URL. The webpage may require JavaScript rendering.")

        return clean_text

    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        raise ValueError(f"Error parsing webpage HTML: {str(e)}")


def scrape_text_from_url(url: str) -> str:
    """Fetch a scheme page: fast static request first, headless browser (Playwright)
    when the page is JavaScript-rendered, blocked (403) or returns almost no text."""
    url = _normalize_url(url)

    static_err, static_text = None, None
    try:
        static_text = _html_to_text(_fetch_static_html(url), url)
        if len(static_text) >= MIN_STATIC_CHARS:
            return static_text
    except ValueError as e:
        if "listing/search page" in str(e) or "Invalid" in str(e):
            raise
        static_err = e

    try:
        rendered = _render_html_playwright(url)
    except Exception as pw_err:  # noqa: BLE001
        if static_text and len(static_text) >= 15:
            return static_text
        reason = static_err or "page returned too little text"
        raise ValueError(f"{reason}. Browser rendering also failed: {pw_err}")

    return _html_to_text(rendered, url)
