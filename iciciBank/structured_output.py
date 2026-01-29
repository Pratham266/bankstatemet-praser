def generate_structured_output(grouped_transactions):
    """
    Converts ICICI transaction rows into final structured JSON.
    """

    structured_data = []

    for row in grouped_transactions:
        (
            sr_no,
            txn_id,
            value_date,
            txn_date,
            cheque_ref,
            remarks,
            withdraw,
            deposit,
            balance
        ) = row

        withdraw = withdraw.replace(",", "").strip()
        deposit = deposit.replace(",", "").strip()
        balance = balance.replace(",", "").strip()

        txn_type = "UNKNOWN"
        amount = "0.00"

        if withdraw and withdraw.upper() != "NA":
            txn_type = "DEBIT"
            amount = withdraw
        elif deposit and deposit.upper() != "NA":
            txn_type = "CREDIT"
            amount = deposit

        structured_data.append({
            "date": txn_date,
            "txnId": txn_id,
            "remarks": remarks,
            "amount": amount,
            "balance": balance,
            "type": txn_type
        })

    return structured_data
