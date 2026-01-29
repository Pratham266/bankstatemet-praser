import re

DATE_RE = re.compile(r"\d{2}-[A-Za-z]{3}-\d{4}")


def normalize_cell(val):
    return " ".join(str(val or "").split())


def refactor_date(val):
    if not val:
        return val

    val = normalize_cell(val)
    # Fix: 01-May- 2024 → 01-May-2024
    val = re.sub(r"([A-Za-z]{3})-\s+(\d{4})", r"\1-\2", val)
    return val


def is_date(val):
    return bool(val and DATE_RE.fullmatch(val))


def is_empty_row(row):
    return all(not c for c in row)


def group_transactions(pages, page_number=None):
    grouped = []

    for page in pages:
        for row in page:
            # Normalize row
            row = [normalize_cell(c) for c in row]

            if len(row) < 9:
                continue

            if is_empty_row(row):
                continue

            # Skip header
            if row[0].lower().startswith("sr") or row[1].lower().startswith("tran"):
                continue

            # 🔧 FIX DATE before validation
            row[2] = refactor_date(row[2])  # Value Date
            row[3] = refactor_date(row[3])  # Transaction Date (safe)

            # ✅ Validate on Value Date
            if not is_date(row[2]):
                continue

            grouped.append(row)

    return grouped
