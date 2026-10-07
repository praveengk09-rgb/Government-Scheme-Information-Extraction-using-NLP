import re
from typing import Dict, List, Optional


NOT_AVAILABLE = "Not available in the provided document."


SCHEME_FIELDS = [
    "Scheme Name",
    "Objective / Purpose",
    "Eligibility Criteria",
    "Key Benefits / Financial Assistance",
    "Required Documents",
    "Application Procedure",
    "Application Deadline",
    "Department / Ministry",
    "Target Beneficiaries",
]


# English + Marathi heading patterns
FIELD_HEADINGS = {
    "Objective / Purpose": [
        r"SCHEME OBJECTIVE",
        r"OBJECTIVE",
        r"OBJECTIVES",
        r"PURPOSE",
        r"AIM",
        r"ABOUT THE SCHEME",
        r"VISION",
        r"GOAL",
        r"उद्दिष्ट",
        r"उद्दिष्ट / हेतू",
        r"हेतू",
        r"योजनेचा उद्देश",
    ],

    "Eligibility Criteria": [
        r"ELIGIBILITY CRITERIA",
        r"ELIGIBILITY",
        r"WHO CAN APPLY",
        r"ELIGIBLE APPLICANTS",
        r"ELIGIBLE BENEFICIARIES",
        r"ELIGIBLE BENIFICIARIES",
        r"CONDITIONS",
        r"पात्रता निकष",
        r"पात्रता",
        r"पात्र लाभार्थी",
        r"कोण अर्ज करू शकतो",
        r"अर्जदाराची पात्रता",
    ],

    "Key Benefits / Financial Assistance": [
        r"KEY BENEFITS\s*(?:&|AND)?\s*FINANCIAL ASSISTANCE",
        r"KEY BENEFITS",
        r"BENEFITS",
        r"FINANCIAL ASSISTANCE",
        r"FINANCIAL SUPPORT",
        r"BENEFIT",
        r"ASSISTANCE",
        r"GRANT",
        r"SUBSIDY",
        r"INCENTIVES",
        r"मुख्य लाभ\s*/?\s*आर्थिक सहाय्य",
        r"मुख्य लाभ",
        r"लाभ",
        r"आर्थिक सहाय्य",
        r"आर्थिक मदत",
        r"अनुदान",
        r"अर्थसहाय्य",
    ],

    "Required Documents": [
        r"REQUIRED DOCUMENTS",
        r"DOCUMENTS REQUIRED",
        r"DOCUMENTS NEEDED",
        r"DOCUMENTS",
        r"ENCLOSURES",
        r"CHECKLIST",
        r"आवश्यक कागदपत्रे",
        r"आवश्यक दस्तऐवज",
        r"कागदपत्रे आवश्यक",
        r"कागदपत्रे",
        r"आवश्यक दस्तऐवज",
    ],

    "Application Procedure": [
        r"APPLICATION PROCEDURE",
        r"HOW TO APPLY",
        r"APPLICATION PROCESS",
        r"PROCEDURE",
        r"PROCESS",
        r"REGISTRATION",
        r"ONLINE APPLICATION",
        r"अर्ज करण्याची प्रक्रिया",
        r"अर्ज प्रक्रिया",
        r"अर्ज करण्याची पद्धत",
        r"अर्ज कसा करावा",
        r"अर्ज प्रक्रिया",
        r"नोंदणी प्रक्रिया",
    ],

    "Application Deadline": [
        r"APPLICATION DEADLINE",
        r"DEADLINE\s*(?:&|AND)?\s*TARGETS",
        r"DEADLINE",
        r"LAST DATE",
        r"CLOSING DATE",
        r"DUE DATE",
        r"END DATE",
        r"VALID UNTIL",
        r"अर्जाची अंतिम तारीख",
        r"अंतिम तारीख",
        r"अर्ज करण्याची अंतिम तारीख",
        r"शेवटची तारीख",
        r"अंतिम दिनांक",
    ],

    "Department / Ministry": [
        r"DEPARTMENT\s*/\s*MINISTRY",
        r"DEPARTMENT",
        r"MINISTRY",
        r"IMPLEMENTING AGENCY",
        r"ISSUED BY",
        r"विभाग\s*/\s*मंत्रालय",
        r"विभाग",
        r"मंत्रालय",
        r"अंमलबजावणी विभाग",
        r"अंमलबजावणी करणारा विभाग",
    ],

    "Target Beneficiaries": [
        r"TARGET BENEFICIARIES",
        r"BENEFICIARIES",
        r"TARGET GROUP",
        r"TARGET AUDIENCE",
        r"COVERED GROUP",
        r"WHO BENEFITS",
        r"लक्षित लाभार्थी",
        r"लक्ष्यित लाभार्थी",
        r"लाभार्थी",
        r"लक्ष्यित गट",
        r"लक्षित गट",
        r"कोणाला लाभ मिळेल",
    ],
}


def empty_result() -> Dict[str, str]:
    """Return an empty scheme information dictionary."""
    return {field: NOT_AVAILABLE for field in SCHEME_FIELDS}


def detect_language(text: str) -> str:
    """
    Detect English vs Marathi using the presence of Devanagari characters.

    Returns:
        'Marathi' if substantial Devanagari text is present,
        otherwise 'English'.
    """
    if not text or not text.strip():
        return "Unknown"

    devanagari_chars = re.findall(r"[\u0900-\u097F]", text)
    latin_chars = re.findall(r"[A-Za-z]", text)

    devanagari_count = len(devanagari_chars)
    latin_count = len(latin_chars)

    if devanagari_count == 0 and latin_count == 0:
        return "Unknown"

    if devanagari_count > latin_count * 0.15:
        return "Marathi"

    return "English"


def clean_extracted_value(value: Optional[str]) -> str:
    """Clean extracted text while preserving Marathi and English characters."""
    if not value:
        return NOT_AVAILABLE

    value = value.strip()

    # Remove leading numbering such as:
    # 1. Text
    # 2) Text
    # 3 - Text
    value = re.sub(
        r"^\s*\d{1,2}\s*[\.\)\-:]\s*",
        "",
        value
    )

    # Remove leading bullets
    value = re.sub(
        r"^\s*[-•▪●*]\s*",
        "",
        value
    )

    # Remove leading colon/dashes
    value = re.sub(r"^[\s:\-]+", "", value)

    # Normalize whitespace
    lines = [
        line.strip()
        for line in value.splitlines()
        if line.strip()
    ]

    cleaned = " ".join(lines)

    # Normalize repeated spaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if len(cleaned) < 3:
        return NOT_AVAILABLE

    return cleaned


def normalize_heading_line(line: str) -> str:
    """Normalize a heading line for comparison."""
    line = line.strip()

    # Remove numbering
    line = re.sub(
        r"^\s*\d{1,2}\s*[\.\)\-:]\s*",
        "",
        line
    )

    # Remove trailing colon/dash
    line = re.sub(r"[:\-]+$", "", line).strip()

    return line


def heading_matches(line: str, patterns: List[str]) -> bool:
    """
    Check whether a line matches any known English/Marathi heading.
    """
    normalized = normalize_heading_line(line)

    for pattern in patterns:
        if re.fullmatch(pattern, normalized, flags=re.IGNORECASE):
            return True

    return False


def find_heading_line(
    lines: List[str],
    patterns: List[str]
) -> Optional[int]:
    """Return the line index where a heading occurs."""
    for index, line in enumerate(lines):
        if heading_matches(line, patterns):
            return index

    return None


def extract_heading_section(
    lines: List[str],
    field: str
) -> Optional[str]:
    """
    Extract content after a recognized heading until the next
    recognized scheme heading.
    """

    patterns = FIELD_HEADINGS[field]

    start_index = find_heading_line(lines, patterns)

    if start_index is None:
        return None

    content_lines = []

    for index in range(start_index + 1, len(lines)):

        current_line = lines[index]

        # Stop when another known field heading is reached.
        is_next_heading = False

        for other_field, other_patterns in FIELD_HEADINGS.items():
            if other_field == field:
                continue

            if heading_matches(current_line, other_patterns):
                is_next_heading = True
                break

        if is_next_heading:
            break

        content_lines.append(current_line)

    if not content_lines:
        return None

    return cap_text(" ".join(content_lines))


def extract_scheme_name(lines: List[str]) -> Optional[str]:
    """
    Extract scheme name from explicit heading or early prominent lines.
    Supports English and Marathi.
    """

    # Explicit English heading
    name_patterns = [
        r"SCHEME NAME",
        r"NAME OF THE SCHEME",
        r"TITLE OF SCHEME",
        r"SCHEME NOTIFICATION",
        r"योजनेचे नाव",
        r"योजनेचे शीर्षक",
    ]

    index = find_heading_line(lines, name_patterns)

    if index is not None and index + 1 < len(lines):
        return lines[index + 1]

    # Look for common scheme-name words
    for line in lines[:10]:

        if re.search(
            r"\b(?:SCHEME|YOJANA|YOJNA|ABHIYAN|MISSION|PROGRAMME|PROGRAM|SUPPORT)\b",
            line,
            re.IGNORECASE,
        ):
            if not re.match(
                r"^(GOVERNMENT OF|DEPARTMENT OF|MINISTRY OF)",
                line,
                re.IGNORECASE,
            ):
                return line

        # Marathi scheme-name detection
        if re.search(
            r"(योजना|अभियान|मिशन|कार्यक्रम)",
            line
        ):
            return line

    # Fallback: first meaningful line
    for line in lines[:5]:
        if len(line) > 5 and len(line) < 150:
            return line

    return None


MAX_FIELD_CHARS = 450


def split_sentences(lines: List[str]) -> List[str]:
    """Join wrapped lines, but keep short/heading-like lines as their own segment."""
    blocks, buf = [], []
    for ln in lines:
        buf.append(ln)
        if re.search(r"[:\-]\s*$", ln) or (len(ln) <= 40 and not re.search(r"[,.।]$", ln)):
            blocks.append(" ".join(buf)); buf = []
    if buf:
        blocks.append(" ".join(buf))
    out = []
    for blk in blocks:
        for p in re.split(r"(?<=[.।!?;])\s+|\s+(?=\d{1,2}[.)]\s)", blk):
            p = re.sub(r"^\s*\d{1,2}[.)]\s*", "", p).strip()
            if len(p) > 8:
                out.append(p)
    return out


def cap_text(text: str, limit: int = MAX_FIELD_CHARS) -> str:
    """Trim to the limit at a sentence/word boundary."""
    if len(text) <= limit:
        return text
    cut = text[:limit]
    boundary = max(cut.rfind("।"), cut.rfind(". "), cut.rfind("; "))
    cut = cut[: boundary + 1] if boundary > limit * 0.5 else cut.rsplit(" ", 1)[0]
    return cut.rstrip() + " …"


def fallback_search(
    lines: List[str],
    keywords: List[str],
    max_matches: int = 3
) -> Optional[str]:
    """Keyword fallback: best-scoring short sentences, in document order, capped."""
    sentences = split_sentences(lines)
    scored = []
    for idx, sent in enumerate(sentences):
        low = sent.lower()
        score = sum(1 for k in keywords if k.lower() in low)
        if score and len(sent) <= 320:
            scored.append((score, idx, sent))
    if not scored:
        return None
    top = sorted(scored, key=lambda t: (-t[0], t[1]))[:max_matches]
    top.sort(key=lambda t: t[1])
    return cap_text(" ".join(t[2] for t in top))


def refine_scheme_name(name: Optional[str], lines: List[str]) -> Optional[str]:
    """Shorten sentence-like titles to the actual scheme name."""
    title = " ".join(lines[:4])
    m = re.search(r"((?:\S+\s+){0,6}?)\S*योजन\S*", title)
    if m and m.group(1).strip():
        keep = []
        for w in reversed(m.group(1).split()):
            if keep and re.search(r"(ऱ्या|च्या|ाना|ील|ना)$", w):
                break
            if re.search(r"(ऱ्या|च्या)$", w):
                break
            keep.append(w)
        if keep:
            return " ".join(reversed(keep)) + " योजना"
    if name:
        name = re.sub(r"^(SCHEME NOTIFICATION|SCHEME NAME|NAME OF THE SCHEME)\s*[:\-]\s*", "", name, flags=re.I)
        return cap_text(name, 150)
    return name


def extract_department(lines: List[str]) -> Optional[str]:
    text = " ".join(lines[:15])
    m = re.search(r"((?:महाराष्ट्र शासन|भारत सरकार)?\s*[\u0900-\u097F ,]{3,60}?(?:विभाग|मंत्रालय))", text)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip().replace("महाराष्ट्र शासन ", "महाराष्ट्र शासन – ")
    return None


def extract_scheme_info(text: str) -> Dict[str, str]:
    """
    Extract the nine required government-scheme fields.

    Supports:
    - English headings
    - Marathi headings
    - Heading-based extraction
    - Keyword-based fallback
    - Basic date extraction
    - Marathi language detection
    """

    result = empty_result()

    if not text or not isinstance(text, str) or not text.strip():
        return result

    raw_text = text.strip()

    # Normalize line breaks
    raw_text = raw_text.replace("\r\n", "\n")
    raw_text = raw_text.replace("\r", "\n")

    lines = [
        line.strip()
        for line in raw_text.splitlines()
        if line.strip()
    ]

    if not lines:
        return result

    # ---------------------------------------------------------
    # 1. Scheme Name
    # ---------------------------------------------------------

    scheme_name = extract_scheme_name(lines)

    result["Scheme Name"] = clean_extracted_value(refine_scheme_name(scheme_name, lines))

    # ---------------------------------------------------------
    # 2. Objective / Purpose
    # ---------------------------------------------------------

    objective = extract_heading_section(
        lines,
        "Objective / Purpose"
    )

    if not objective:

        objective = fallback_search(
            lines,
            [
                "aims to",
                "objective",
                "purpose",
                "designed to",
                "launched to",
                "उद्देश",
                "हेतू",
                "उद्दिष्ट",
                "मुख्य उद्दिष्ट",
                "उद्देश",
                "गुणवत्तेत वाढ",
            ],
        )

    result["Objective / Purpose"] = clean_extracted_value(
        objective
    )

    # ---------------------------------------------------------
    # 3. Eligibility
    # ---------------------------------------------------------

    eligibility = extract_heading_section(
        lines,
        "Eligibility Criteria"
    )

    if not eligibility:

        eligibility = fallback_search(
            lines,
            [
                "eligible",
                "eligibility",
                "citizen",
                "age",
                "income",
                "resident",
                "पात्र",
                "पात्रता",
                "नागरिक",
                "वय",
                "उत्पन्न",
                "रहिवासी",
                "वार्षिक उत्पन्न",
                "लाख",
                "अनुज्ञेय",
                "निकष",
            ],
        )

    result["Eligibility Criteria"] = clean_extracted_value(
        eligibility
    )

    # ---------------------------------------------------------
    # 4. Benefits
    # ---------------------------------------------------------

    benefits = extract_heading_section(
        lines,
        "Key Benefits / Financial Assistance"
    )

    if not benefits:

        benefits = fallback_search(
            lines,
            [
                "benefit",
                "financial assistance",
                "financial support",
                "subsidy",
                "grant",
                "₹",
                "rs.",
                "inr",
                "आर्थिक सहाय्य",
                "आर्थिक मदत",
                "लाभ",
                "अनुदान",
                "रुपये",
                "निर्वाह भत्ता",
                "शिक्षण फी",
                "शिक्षण शुल्क",
                "परीक्षा शुल्क",
            ],
        )

    result["Key Benefits / Financial Assistance"] = clean_extracted_value(
        benefits
    )

    # ---------------------------------------------------------
    # 5. Required Documents
    # ---------------------------------------------------------

    documents = extract_heading_section(
        lines,
        "Required Documents"
    )

    if not documents:

        documents = fallback_search(
            lines,
            [
                "aadhaar",
                "aadhar",
                "pan card",
                "certificate",
                "bank account",
                "address proof",
                "photo",
                "आधार",
                "प्रमाणपत्र",
                "बँक खाते",
                "बँक तपशील",
                "रहिवासी प्रमाणपत्र",
                "उत्पन्न प्रमाणपत्र",
                "कागदपत्र",
            ],
        )

    result["Required Documents"] = clean_extracted_value(
        documents
    )

    # ---------------------------------------------------------
    # 6. Application Procedure
    # ---------------------------------------------------------

    procedure = extract_heading_section(
        lines,
        "Application Procedure"
    )

    if not procedure:

        procedure = fallback_search(
            lines,
            [
                "apply online",
                "application",
                "portal",
                "register",
                "submit",
                "official website",
                "अर्ज",
                "ऑनलाइन",
                "पोर्टल",
                "नोंदणी",
                "सबमिट",
                "कागदपत्रे अपलोड",
                "ऑनलाईन अर्ज",
                "महाडीबीटी",
                "डीबीटी",
            ],
        )

    result["Application Procedure"] = clean_extracted_value(
        procedure
    )

    # ---------------------------------------------------------
    # 7. Deadline
    # ---------------------------------------------------------

    deadline = extract_heading_section(
        lines,
        "Application Deadline"
    )

    if not deadline:
        near = re.search(
            r"(?:deadline|last date|closing date|due date|अंतिम (?:तारीख|दिनांक)|शेवटची तारीख|मुदत)"
            r".{0,80}?(\d{1,2}[\/\-. ](?:\d{1,2}|[A-Za-z]+)[\/\-. ]\d{4})",
            raw_text, re.IGNORECASE | re.DOTALL,
        )
        if near:
            deadline = near.group(1)

    if not deadline:
        deadline = fallback_search(
            lines,
            ["त्याच दिवशी", "अंतिम तारीख", "अंतिम दिनांक", "मुदत", "last date", "deadline"],
            max_matches=1,
        )

    result["Application Deadline"] = clean_extracted_value(
        deadline
    )

    # ---------------------------------------------------------
    # 8. Department / Ministry
    # ---------------------------------------------------------

    department = extract_heading_section(
        lines,
        "Department / Ministry"
    )

    if not department:
        department = extract_department(lines)

    if not department:

        department = fallback_search(
            lines,
            [
                "ministry",
                "department",
                "government",
                "मंत्रालय",
                "विभाग",
                "महाराष्ट्र शासन",
                "भारत सरकार",
                "सामाजिक न्याय",
                "सहाय्य विभाग",
            ],
        )

    result["Department / Ministry"] = clean_extracted_value(
        department
    )

    # ---------------------------------------------------------
    # 9. Target Beneficiaries
    # ---------------------------------------------------------

    beneficiaries = extract_heading_section(
        lines,
        "Target Beneficiaries"
    )

    if not beneficiaries:
        m = re.search(r"((?:\S+\s+){1,3}(?:प्रवर्गातील|प्रवर्गाच्या)\s+\S*विद्यार्थ\S*)", raw_text)
        if m:
            beneficiaries = m.group(1)

    if not beneficiaries:

        beneficiaries = fallback_search(
            lines,
            [
                "beneficiaries",
                "target group",
                "target audience",
                "low-income",
                "unemployed",
                "farmers",
                "women",
                "students",
                "youth",
                "citizens",
                "लाभार्थी",
                "लक्ष्यित",
                "लक्षित",
                "बेरोजगार",
                "शेतकरी",
                "महिला",
                "विद्यार्थी",
                "विद्यार्थ्य",
                "प्रवर्गातील",
                "युवक",
                "कुटुंबे",
                "नागरिक",
            ],
        )

    result["Target Beneficiaries"] = clean_extracted_value(
        beneficiaries
    )

    return result