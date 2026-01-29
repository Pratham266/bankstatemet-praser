import re


DATE_RE = re.compile(r"\d{2}-\d{2}-\d{4}")


def normalize_cell(val):
    # Convert multiline text to single line
    return " ".join(str(val or "").split())


def is_date(val):
    return bool(val and DATE_RE.fullmatch(val))


def is_empty_row(row):
    return all(not c for c in row)


def group_transactions(pages, page_number=None):
    grouped = []

    for page in pages:
        for row in page:
            # Normalize row cells
            row = [normalize_cell(c) for c in row]

            # Expected columns = 7
            if len(row) < 7:
                continue

            if is_empty_row(row):
                continue

            # Skip header
            if row[0].upper().startswith("TRN"):
                continue

            # Validate transaction date
            if not is_date(row[0]):
                continue

            grouped.append(row)

    return grouped
