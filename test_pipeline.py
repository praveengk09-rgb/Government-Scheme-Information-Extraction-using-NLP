import scraper_pdf
import extractor

print("--- TEST 1: DEMO TEXT EXTRACTION ---")
demo_text = """GOVERNMENT OF INDIA
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

result_demo = extractor.extract_scheme_info(demo_text)
assert result_demo["Scheme Name"] == "GOVERNMENT EMPLOYMENT SUPPORT SCHEME (GESS-2026)", f"Got: {result_demo['Scheme Name']}"
assert "50,000" in result_demo["Key Benefits / Financial Assistance"]
assert "Aadhaar Card" in result_demo["Required Documents"]
print("✓ Demo Text Extraction passed successfully!")

print("\n--- TEST 2: UNSTRUCTURED TEXT WITH MISSING FIELDS ---")
sparse_text = """
State Solar Energy Assistance Notice
Objective: Provide solar panels to rural households.
Eligibility: Families residing in rural areas with electricity bill under 100 units.
"""
result_sparse = extractor.extract_scheme_info(sparse_text)
print("Scheme Name:", result_sparse["Scheme Name"])
print("Objective:", result_sparse["Objective / Purpose"])
print("Deadline:", result_sparse["Application Deadline"])
assert result_sparse["Application Deadline"] == "Not available in the provided document."
assert result_sparse["Required Documents"] == "Not available in the provided document."
print("✓ Sparse Text Handling & Fallback passed successfully!")

print("\nALL BACKEND UNIT TESTS PASSED SUCCESSFULLY!")
