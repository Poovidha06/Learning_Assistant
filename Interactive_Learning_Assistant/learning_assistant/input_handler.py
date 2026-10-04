import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup

# Optional better scrapers
try:
    from newspaper import Article
    NEWSPAPER = True
except ImportError:
    NEWSPAPER = False

try:
    from readability import Document
    READABILITY = True
except ImportError:
    READABILITY = False


# ------------------------------
# PDF Extraction
# ------------------------------
def extract_text_from_pdf(file):
    text = ""
    doc = fitz.open(stream=file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text()
    return text.strip()


# ------------------------------
# Web URL Extraction
# ------------------------------
def extract_text_from_url(url: str) -> str:
    try:
        # --- Method 1: Newspaper3k (best for articles/news) ---
        if NEWSPAPER:
            article = Article(url)
            article.download()
            article.parse()
            return article.text.strip()

        # --- Method 2: Readability-lxml (clean boilerplate) ---
        if READABILITY:
            response = requests.get(url, timeout=10)
            doc = Document(response.text)
            return doc.summary(html_clean=True)

        # --- Method 3: Raw BeautifulSoup fallback ---
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        for script in soup(["script", "style", "header", "footer", "nav", "aside"]):
            script.extract()

        # Pick largest text block (heuristic)
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        if paragraphs:
            return "\n\n".join(paragraphs)

        return soup.get_text(" ", strip=True)

    except Exception as e:
        return f"❌ Error fetching URL: {e}"
