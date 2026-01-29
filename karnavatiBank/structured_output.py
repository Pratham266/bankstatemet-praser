import re


def extract_txn_ref(narration):
    if not narration:
        return None

    patterns = [
        r"IMPS\s+(\d+)",
        r"NEFT\s+([A-Z0-9]+)",
        r"RTGS\s+([A-Z0-9]+)",
        r"UPI\s+(\d+)",
    ]

    for pat in patterns:
        m = re.search(pat, narration)
        if m:
            return m.group(1)

    return None


def generate_structured_output(grouped_transactions):
    structured_data = []

    for row in grouped_transactions:
        (
            txn_date,
            value_date,
            narration,
            chq_ref,
            debit,
            credit,
            balance
        ) = row

        debit = debit.replace(",", "").strip()
        credit = credit.replace(",", "").strip()
        balance = balance.replace(",", "").strip()

        txn_type = "UNKNOWN"
        amount = "0.00"

        if debit:
            txn_type = "DEBIT"
            amount = debit
        elif credit:
            txn_type = "CREDIT"
            amount = credit

        # ✅ FIXED txnId logic
        ref_from_narration = extract_txn_ref(narration)

        if ref_from_narration:
            txn_id = ref_from_narration
        else:
            txn_id = f"{txn_date}_{amount}_{balance}"

        structured_data.append({
            "date": txn_date,
            "txnId": txn_id,
            "remarks": narration,
            "amount": amount,
            "balance": balance,
            "type": txn_type
        })

    return structured_data
