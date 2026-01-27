def generate_structured_output(grouped_transactions):
    """
    Converts a list of grouped transaction arrays into a list of structured dictionaries.
    
    Args:
        grouped_transactions (list): List of list of strings, e.g.,
        [
            [
                 "01 Jun 2025 11:20 AM", 
                 "UPI/SHIVAM...", 
                 "UPI-...", 
                 "-500.00", 
                 "5,44,651.07"
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
        balance = row[4]
        
        # Calculate Type
        # Logic: If amount contains '-', it's DEBIT. If '+', it's CREDIT.
        # Fallback: parse float.
        check_amt = amount_str.replace(',', '').strip()
        if '-' in check_amt:
            txn_type = "DEBIT"
        elif '+' in check_amt:
            txn_type = "CREDIT"
        else:
            # If no sign, assume valid positive number might be credit? 
            # Or usually bank statements without sign are ambiguous, but typically credit if in credit col.
            # Here we have a single column with signs.
            try:
                val = float(check_amt)
                if val < 0:
                    txn_type = "DEBIT"
                else:
                    txn_type = "CREDIT"
            except:
                txn_type = "UNKNOWN"
        
        structured_data.append({
            "date": txn_date,
            "txnId": txn_id,
            "remarks": remarks,
            "amount": amount_str.replace("-", "").replace("+", ""),
            "balance": balance,
            "type": txn_type
        })
        
    return structured_data
