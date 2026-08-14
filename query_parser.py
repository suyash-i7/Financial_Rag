import re


def parse_query(question):

    # -----------------------------
    # Detect all quarters
    # -----------------------------

    matches = re.findall(
        r"\bQ([1-4])\s*FY(\d{2,4})\b",
        question,
        re.IGNORECASE
    )

    quarters = []

    for quarter, year in matches:

        if len(year) == 2:
            year = "20" + year

        end_year = str(year)[-2:]
        start_year = int(year) - 1

        quarters.append(
            f"Q{quarter} FY{start_year}-{end_year}"
        )

    # Remove duplicates
    quarters = list(dict.fromkeys(quarters))


    # -----------------------------
    # Detect entity
    # -----------------------------

    entity = None

    question_lower = question.lower()

    if "jio platforms" in question_lower:
        entity = "Jio Platforms"

    elif "jiostar" in question_lower:
        entity = "JioStar"

    elif "oil to chemicals" in question_lower or "o2c" in question_lower:
        entity = "O2C"

    elif "reliance industries" in question_lower or "ril" in question_lower:
        entity = "Reliance Industries"


    # -----------------------------
    # Detect metric
    # -----------------------------

    metric = None

    if "ebitda margin" in question_lower:
        metric = "EBITDA Margin"

    elif "ebitda" in question_lower:
        metric = "EBITDA"

    elif "profit after tax" in question_lower or "pat" in question_lower:
        metric = "Profit After Tax"

    elif "revenue" in question_lower:
        metric = "Revenue"

    elif "capital expenditure" in question_lower or "capex" in question_lower:
        metric = "Capital Expenditure"


    # -----------------------------
    # Detect intent
    # -----------------------------

    if "compare" in question_lower:
        intent = "comparison"

    elif "what businesses" in question_lower:
        intent = "business_overview"

    elif metric:
        intent = "financial_metric"

    else:
        intent = "general"


    return {
        "entity": entity,
        "quarters": quarters,
        "metric": metric,
        "intent": intent
    }


# -----------------------------
# TEST
# -----------------------------

if __name__ == "__main__":

    questions = [
        "What was Jio Platforms EBITDA in Q4 FY26?",
        "What was Jio Platforms revenue in Q4 FY26?",
        "What was Jio Platforms EBITDA in Q1 FY27?",
        "Compare Jio Platforms EBITDA in Q4 FY26 with Q4 FY25.",
        "What businesses does Reliance Industries operate?",
        "What was Reliance Industries capital expenditure in Q4 FY26?"
    ]

    for question in questions:

        print("\nQUESTION:")
        print(question)

        print("PARSED:")
        print(parse_query(question))