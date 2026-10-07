import scraper_pdf
import extractor

sample_text = """GOVERNMENT OF INDIA
DEPARTMENT OF RURAL DEVELOPMENT

SCHEME NOTIFICATION: GOVERNMENT EMPLOYMENT SUPPORT SCHEME (GESS-2026)

1. SCHEME OBJECTIVE:
The Government Employment Support Scheme aims to provide financial assistance and employment support to eligible citizens across rural and semi-urban sectors.

2. ELIGIBILITY CRITERIA:
Indian citizens satisfying the prescribed age and income criteria are eligible to apply.

3. KEY BENEFITS & FINANCIAL ASSISTANCE:
Financial assistance up to ₹50,000 disbursed directly via DBT.

4. REQUIRED DOCUMENTS:
Aadhaar Card, income certificate, bank account details and address proof.

5. APPLICATION PROCEDURE:
Apply through the official online portal and upload the required documents.

6. DEADLINE & TARGETS:
Application Deadline: 31 December 2026.
Target Beneficiaries: Eligible low-income households and unemployed citizens.
"""

extracted = extractor.extract_scheme_info(sample_text)
print("=== EXTRACTED FIELD TEST RESULTS ===")
for k, v in extracted.items():
    print(f"{k}: {v}")

print("\n=== TESTING URL SCRAPER ===")
try:
    url_text = scraper_pdf.scrape_text_from_url("https://example.com")
    print(f"Scraped {len(url_text)} characters from example.com successfully.")
    url_extracted = extractor.extract_scheme_info(url_text)
    print("URL Scheme Name:", url_extracted["Scheme Name"])
except Exception as e:
    print("URL Scrape Note:", e)
