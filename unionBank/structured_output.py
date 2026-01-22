def generate_structured_output(grouped_transactions):
    """
    Converts a list of grouped transaction arrays into a list of structured dictionaries.
    
    Args:
        grouped_transactions (list): List of list of strings, e.g.,
        [
            [
                "16-12-2025",
                "V53604535",
                "UPIAR/535043861014/DR/Maheshwa/YESB/paytmqrtrmh3i2",
                "60.0(Dr)",
                "1309.13(Cr)",
            ], 
            ...
        ]
        
    Returns:
        list: List of dictionaries with keys: date, txnId, remarks, amount, balance, type.
    """
    structured_data = []
    
    for row in grouped_transactions:
        if not row or len(row) < 5:
            continue
            
        txn_date = row[0]
        remarks = row[1]
        txn_id = row[2]
        amount_str = row[3]
        balance = row[4].replace('(Cr)', '').replace('(Dr)', '')
        
        # Calculate Type
        # Logic: If amount contains 'Dr', it's DEBIT. If 'Cr', it's CREDIT.
        # Fallback: parse float.
        check_amt = amount_str.replace(',', '').strip()
        if 'Dr' in check_amt:
            txn_type = "DEBIT"
            amount_str = "-" + amount_str.replace('(Dr)', '')
        elif 'Cr' in check_amt:
            txn_type = "CREDIT"
            amount_str = "+" + amount_str.replace('(Cr)', '')
        else:
            txn_type = "UNKNOWN"
        

        structured_data.append({
            "date": txn_date,
            "txnId": txn_id,
            "remarks": remarks,
            "amount": amount_str,
            "balance": balance,
            "type": txn_type
        })
        
    return structured_data
