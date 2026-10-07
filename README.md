# 🏛️ Government Scheme Information Extraction using NLP

An interactive, modern Streamlit web dashboard for extracting, structuring, and analyzing key parameters from Indian Government Scheme documents using Natural Language Processing (NLP).

---

## 📌 Project Overview

Government Scheme notifications and policy guidelines are often length, unstructured, and dense. This project provides a clean academic and professional dashboard designed to automatically parse scheme documents (PDF or Web URLs) and extract 9 key parameters into structured information cards and JSON formats:

1. **Scheme Name**
2. **Objective / Purpose**
3. **Eligibility Criteria**
4. **Key Benefits / Financial Assistance**
5. **Required Documents**
6. **Application Procedure**
7. **Application Deadline**
8. **Department / Ministry**
9. **Target Beneficiaries**

---

## 📁 Project Structure

```text
government-scheme-nlp/
│
├── app.py              # Main Streamlit application UI & workflow
├── requirements.txt    # Python dependencies
└── README.md           # Documentation & project guide
```

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
Ensure you have **Python 3.8+** installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
Launch the Streamlit web application:
```bash
streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`.

---

## 🎨 Application UI & Features

* **Tab 1: Input Document**
  * Support PDF upload (`st.file_uploader`)
  * Support Website URL input (`st.text_input`)
  * **🎯 Try Demo** button for instant demonstration without file uploads
  * Input validation & graceful error handling

* **Tab 2: Extracted Scheme Data**
  * 9 styled information cards displaying key scheme attributes
  * Formatted JSON output view (`st.json`)
  * One-click JSON export button (`st.download_button`)

* **Tab 3: NLP Analytics**
  * Live text metrics (Characters, Words, Sentences, Tokens, Unique Tokens)
  * Language Detection badge
  * Interactive Visual Pipeline diagram from Text Input to Structured Scheme Data

* **Sidebar Panel**
  * Project overview & current document load status
  * Technologies stack tags
  * Planned future NLP modules roadmap

---

## 🔮 Future NLP Pipeline Integration

Planned modules for subsequent backend iterations:
* Text Preprocessing & Cleaning
* NLTK / spaCy Stemming & Lemmatization
* N-Gram Frequency Analysis
* MLE Probability & Next Word Prediction
* Named Entity Recognition (NER) for Govt Depts & Financial Amounts
* Multilingual Support (Marathi & Hindi Translation)
