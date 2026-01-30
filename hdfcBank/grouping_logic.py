import re
import json


def is_footer_or_summary_row(row):
    text = " ".join(str(c or "").upper() for c in row)

    BLOCK_KEYWORDS = [
        "STATEMENTSUMMARY",
        "OPENINGBALANCE",
        "DRCOUNT",
        "CRCOUNT",
        "DEBITS",
        "CREDITS",
        "GENERATEDON",
        "GENERATEDBY",
        "REQUESTINGBRANCHCODE",
        "COMPUTERGENERATED",
        "NOTREQUIRESIGNATURE",
    ]

    return any(k in text for k in BLOCK_KEYWORDS)


DATE_RE = re.compile(r"\d{2}/\d{2}/\d{2}")
AMOUNT_RE = re.compile(r"[\d,]+\.\d{2}")


def is_date(val):
    return bool(val and DATE_RE.fullmatch(val.strip()))


def is_empty_row(row):
    return all(not str(c).strip() for c in row)


def group_transactions(pages, page_number):
    transactions = []
    current = None

    # Fixed column indexes for THIS layout
    DATE_COL = 0
    NARR_COL = 1
    REF_COL = 2
    VALUE_DT_COL = 3
    WITHDRAW_COL = 4
    DEPOSIT_COL = 5
    BAL_COL = 6

    for page in pages:
        for row in page:

            # Normalize row length
            row = [(c or "").strip() for c in row]
            while len(row) < 7:
                row.append("")

            # Skip garbage / empty rows
            if is_empty_row(row):
                continue

            # Skip header row
            if row[0] == "Date" and "Narration" in row[1]:
                continue

            # ---- TRANSACTION START ----
            if is_date(row[DATE_COL]):
                # Save previous transaction
                if current:
                    transactions.append(current)

                current = {
                    "date": row[DATE_COL],
                    "narration": [],
                    "ref": [],
                    "amount": "",
                    "balance": "",
                }

                # Narration
                if row[NARR_COL]:
                    current["narration"].append(row[NARR_COL])

                # Ref no (may be partial)
                if row[REF_COL]:
                    current["ref"].append(row[REF_COL])

                # Amount
                if row[WITHDRAW_COL]:
                    current["amount"] = "-" + row[WITHDRAW_COL]
                elif row[DEPOSIT_COL]:
                    current["amount"] = "+" + row[DEPOSIT_COL]

                # Balance
                if row[BAL_COL]:
                    current["balance"] = row[BAL_COL]

            # ---- CONTINUATION ROW ----
            elif current:
                # 🚫 STOP garbage from last page
                if is_footer_or_summary_row(row):
                    continue
                if row[NARR_COL]:
                    current["narration"].append(row[NARR_COL])

                if row[REF_COL]:
                    current["ref"].append(row[REF_COL])

        # end rows
    # end pages

    if current:
        transactions.append(current)

    # ---- FINAL NORMALIZATION ----
    final_rows = []
    for t in transactions:
        final_rows.append([
            t["date"],
            " ".join(t["narration"]),
            "".join(t["ref"]),
            t["amount"],
            t["balance"]
        ])

    # Optional debug dump
    # with open(f"page_{page_number}_grouped.json", "w") as f:
    #     json.dump(final_rows, f, indent=2)

    return final_rows