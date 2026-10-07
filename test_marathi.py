import extractor, scraper_pdf

text = open("sample_gr_marathi.txt", encoding="utf-8").read()
r = extractor.extract_scheme_info(text)

assert r["Scheme Name"] == "भारत सरकार मॅट्रिकोत्तर शिष्यवृत्ती योजना", r["Scheme Name"]
assert "2.50 लाख" in r["Eligibility Criteria"]
assert "निर्वाह भत्ता" in r["Key Benefits / Financial Assistance"]
assert "सामाजिक न्याय व विशेष सहाय्य विभाग" in r["Department / Ministry"]
assert "त्याच दिवशी" in r["Application Deadline"]
assert all(len(v) <= 520 for v in r.values()), "a field is too long"
assert not scraper_pdf.looks_garbled(text)
assert scraper_pdf.looks_garbled("(cid:290)" * 20)
print("✓ Marathi GR extraction + garble detection passed")
