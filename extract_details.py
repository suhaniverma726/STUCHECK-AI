import re


def extract_student_details(text):

    details = {}

    # ======================================
    # Clean OCR Text
    # ======================================

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()


    # ======================================
    # Student Name
    # ======================================

    name_patterns = [

        # Example:
        # (This je to certify that) SUHANI VERMA
        r"certif\w*\s+that\)?\s*([A-Z][A-Z ]{2,40}?)(?=\s+(?:2|has|who|was|is|son|daughter|candidate)\b)",

        # Flexible fallback
        r"certif\w*\s+that\)?\s*([A-Z][A-Z ]{2,40})",

    ]

    for pattern in name_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            name = match.group(1).strip()

            # Remove unwanted characters
            name = re.sub(
                r"[^A-Za-z ]",
                "",
                name
            )

            # Remove extra spaces
            name = re.sub(
                r"\s+",
                " ",
                name
            ).strip()

            if len(name) > 2:

                details["Name"] = name.upper()
                break


    # ======================================
    # Certificate Number
    # ======================================

    certificate_patterns = [

        # Example:
        # Certificate No. 38012966
        r"certificate\s*(?:no|number|num)?\.?\s*[:\-]?\s*(\d{6,12})",

        # OCR may have text between Certificate and number
        r"certificate.{0,50}?(\d{6,12})",

    ]

    for pattern in certificate_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            details["Certificate Number"] = match.group(1)
            break


    # ======================================
    # Certificate Number Fallback
    # ======================================

    if "Certificate Number" not in details:

        # Look for an 8-digit number
        # near certificate-related text

        certificate_context = re.search(
            r"certificate.{0,100}",
            text,
            re.IGNORECASE
        )

        if certificate_context:

            number_match = re.search(
                r"\b\d{8}\b",
                certificate_context.group(0)
            )

            if number_match:

                details["Certificate Number"] = (
                    number_match.group(0)
                )


    # ======================================
    # Total Marks
    # ======================================

    marks_patterns = [

        # Example:
        # 142/500
        r"\b(\d{2,3})\s*/\s*500\b",

        # Example:
        # Total Marks 142/500
        r"(?:total\s+marks|marks).{0,30}?(\d{2,3})\s*/\s*500",

    ]

    for pattern in marks_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            details["Total Marks"] = (
                match.group(1) + "/500"
            )

            break


    # ======================================
    # Result
    # ======================================

    passed_match = re.search(
        r"\bPASS(?:ED)?\b",
        text,
        re.IGNORECASE
    )

    failed_match = re.search(
        r"\bFAIL(?:ED)?\b",
        text,
        re.IGNORECASE
    )


    if passed_match:

        details["Result"] = "PASSED"

    elif failed_match:

        details["Result"] = "FAILED"


    # ======================================
    # Return Details
    # ======================================

    return details


# ==========================================
# Standalone Testing
# ==========================================

if __name__ == "__main__":

    from ocr import extract_text

    image_path = "test.jpg.jpeg"

    text = extract_text(image_path)

    print("\n========== STUCHECK AI ==========")
    print("Extracted Document Text:")
    print("================================")
    print(text)

    details = extract_student_details(text)

    print("\n========== STUDENT DETAILS ==========")

    if details:

        for key, value in details.items():

            print(f"{key}: {value}")

    else:

        print("No details found.")