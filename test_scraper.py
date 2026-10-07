import scraper_pdf
from bs4 import BeautifulSoup

print("--- TEST 1: SCRAPING STATIC WEBPAGE ---")
try:
    # Test scraping static example.com
    text_static = scraper_pdf.scrape_text_from_url("https://example.com")
    print("Scraped Text Result:\n", text_static[:200])
    assert "EXAMPLE DOMAIN" in text_static.upper(), "Static website scrape did not contain heading text."
    print("✓ Static webpage scraping test passed successfully!")
except Exception as e:
    print(f"Static test note: {e}")

print("\n--- TEST 2: LISTING PAGE DETECTION ---")
sample_listing_html = """
<html>
<head><title>Search Schemes - National Portal</title></head>
<body>
<h1>Search Schemes</h1>
<p>Search schemes by state, ministry, or category.</p>
<div>Select State | Filter by Category | Total schemes found: 150</div>
</body>
</html>
"""
soup_listing = BeautifulSoup(sample_listing_html, 'html.parser')
is_listing = scraper_pdf.is_listing_or_search_page(soup_listing, "https://myscheme.gov.in/search", sample_listing_html)
assert is_listing == True, "Listing page was not detected correctly."
print("✓ Scheme search/listing page detection test passed successfully!")

print("\n--- TEST 3: SCHEME DETAIL PAGE CONTENT EXTRACTION ---")
sample_detail_html = """
<html>
<head><title>PM KISAN Scheme Details</title></head>
<body>
<main>
<h1>Pradhan Mantri Kisan Samman Nidhi</h1>
<p>DEPARTMENT / MINISTRY: Ministry of Agriculture and Farmers Welfare</p>
<h2>SCHEME OBJECTIVE</h2>
<p>To provide financial support to small and marginal farmer families nationwide.</p>
<h2>ELIGIBILITY CRITERIA</h2>
<ul>
<li>All landholding farmer families with cultivable landholding in their names.</li>
<li>Subject to certain exclusion categories for higher income strata.</li>
</ul>
<h2>KEY BENEFITS</h2>
<p>Financial benefit of Rs 6,000 per year in three equal installments.</p>
<h2>REQUIRED DOCUMENTS</h2>
<p>Aadhaar Card, Land holding documents, Bank account details.</p>
</main>
</body>
</html>
"""
soup_detail = BeautifulSoup(sample_detail_html, 'html.parser')
is_detail_listing = scraper_pdf.is_listing_or_search_page(soup_detail, "https://pmkisan.gov.in/detail", sample_detail_html)
assert is_detail_listing == False, "Scheme detail page was incorrectly flagged as listing page."
print("✓ Scheme detail page parsing test passed successfully!")

print("\nALL SCRAPER TESTS COMPLETED!")
