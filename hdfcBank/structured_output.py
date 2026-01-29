def generate_structured_output(grouped_transactions):
    """
    Converts grouped transaction rows into structured JSON objects.

    Input row format:
    [
        date,
        narration,
        txnId,
        signed_amount,   # "-619.00" or "+100.00"
        balance
    ]
    """

    structured_data = []

    for row in grouped_transactions:
        if not row or len(row) < 5:
            continue

        txn_date = row[0]
        remarks = row[1]
        txn_id = row[2]
        signed_amount = row[3].replace(",", "").strip()
        balance = row[4]

        # Determine type & unsigned amount
        txn_type = "UNKNOWN"
        amount = signed_amount

        if signed_amount.startswith("-"):
            txn_type = "DEBIT"
            amount = signed_amount.replace("-", "")
        elif signed_amount.startswith("+"):
            txn_type = "CREDIT"
            amount = signed_amount.replace("+", "")

        structured_data.append({
            "date": txn_date,
            "txnId": txn_id,
            "remarks": remarks,
            "amount": amount,
            "balance": balance,
            "type": txn_type
        })

    return structured_data