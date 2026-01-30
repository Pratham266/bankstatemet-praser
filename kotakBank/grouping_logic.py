import json
import re

def is_date(text):
    return bool(
        text and re.search(r'\d{2}\s+[A-Z][a-z]{2}\s+\d{4}', text)
    )

def is_time(text):
    return bool(
        text and re.search(r'\d{1,2}:\d{2}\s*(AM|PM)', text)
    )

def normalize(items):
    return ''.join(
        sorted(
            ''.join(sorted(str(v).strip()))
            for v in items
            if str(v).strip()
        )
    )

def is_transaction_start(row,tarnsectionDateIndex):
    """
    Transaction starts ONLY when a DATE is found in row[1].
    """
    if len(row) < 2:
        return False

    col1 = str(row[tarnsectionDateIndex]).strip()

    return is_date(col1)


def group_transactions(pages,page_number):
    """
    Groups raw table rows into grouped transaction blocks.
    Args:
        pages (list): A list of pages, where each page is a list of rows, and each row is a list of cell strings.
    Returns:
        list: A list of transactions, where each transaction is a list of rows that belong to it.
    """
    transactions = []
    current_transaction = []
    
    # Flag to indicate if we have started processing actual transactions (to skip pre-header garbage)
    in_transactions = False
    hashIndex=0
    tarnsectionDateIndex=0
    valuedateIndex=0
    transactionDetailsIndex=0
    chqRefNoIndex=0
    debitCreditIndex=0
    balanceIndex=0

    for page in pages:
        for row in page:
            if not row:
                continue
            
            first_col = str(row[0]).strip()
            
            # # Heuristic: Skip Header Rows
            # # Header typically starts with '#' or contains 'TRANSACTION DATE'
            # expected = ['#', 'TRANSACTION DATE', 'VALUE', 'DATE', 'TRANSACTION DETAILS', 'CHQ / REF NO.', 'DEBIT/CREDIT(₹)', 'BALANCE(₹)']
            # # Create sorted strings for comparison
            # row_normalized = normalize(row)
            # expected_normalized = normalize(expected)
            # # Check if sorted strings match
            
            if first_col == "#" or "TRANSACTION DATE" in [str(c).upper().strip() for c in row]:
                for idx, val in enumerate(row):
                    
                    if str(val).strip() == "#":
                        hashIndex=idx
                    elif "TRANSACTION DATE" in str(val).upper().strip():
                        tarnsectionDateIndex=idx
                    elif "VALUE" in str(val).upper().strip():
                        valuedateIndex=idx
                    elif "DETAILS" in str(val).upper().strip():
                        transactionDetailsIndex=idx
                    elif "CHQ / REF NO." in str(val).upper().strip():
                        chqRefNoIndex=idx
                    elif "DEBIT/CREDIT" in str(val).upper().strip():
                        debitCreditIndex=idx
                    elif "BALANCE" in str(val).upper().strip():
                        balanceIndex=idx
                continue
            
            # Heuristic: New Transaction starts with a date in the first column
            if is_transaction_start(row,tarnsectionDateIndex):
                # If we were building a transaction, save it
                if current_transaction:
                    transactions.append(current_transaction)
                
                # Start new transaction
                current_transaction = [row]
                in_transactions = True
                
            elif in_transactions:
                # If we are inside a transaction handling sequence, subsequent rows 
                # with empty first column are likely continuation rows.
                # Verification: Most extracted tables have empty first col for wrapped text lines.
                
                # We append blindly if first_col is empty. 
                # If there's a row with text in first_col but not a number (e.g. garbage?), 
                # we might need to handle it, but for now assuming strict table structure.
                if not any("tate" in str(cell) or "ment generated on" in str(cell) for cell in row):
                    current_transaction.append(row)
                else:
                    # If first_col is not empty and not a number, what is it?
                    # Could be footer or page number text mistakenly in the column?
                    # For safety, if it looks like garbage, we might ignore or append.
                    # Given the user example, let's treat it as continuation if it doesn't look like a start.
                    pass
            
    # Append the final transaction if exists
    if current_transaction:
        transactions.append(current_transaction)
    # with open(f"page_{page_number}_raw2.json", "w") as f:
    #         json.dump(transactions, f, indent=4)
    # Validation and Processing to merge rows
    merged_transactions = []
    
    for txn_rows in transactions:
        if not txn_rows:
            continue
            
        # Initialize fields
        merged_date = []
        merged_desc = []
        merged_ref = []
        merged_amt = []
        merged_bal = []
        
        for row in txn_rows:
            # Ensure row has enough columns (pad if necessary, though usually extract_tables does it)
            # We need up to index 8
            while len(row) < 9:
                row.append("")
            # Date (Col 1)
            if row[tarnsectionDateIndex] and str(row[tarnsectionDateIndex]).strip():
                merged_date.append(str(row[tarnsectionDateIndex]).strip())
            # Description (Col 4 + Col 5)
            # User wants: array[0][4]+array[0][5] + array[1][4]+array[1][5] ...
            part1 = str(row[transactionDetailsIndex]).strip() if row[transactionDetailsIndex] else ""
            if transactionDetailsIndex + 1 != chqRefNoIndex:
                part2 = str(row[transactionDetailsIndex + 1]).strip() if len(row) > transactionDetailsIndex + 1 and row[transactionDetailsIndex + 1] else ""
            else:
                part2 = ""
            if part1 or part2:
                merged_desc.append(part1 + part2)
                
            # Ref (Col 6)
            if row[chqRefNoIndex] and str(row[chqRefNoIndex]).strip():
                merged_ref.append(str(row[chqRefNoIndex]).strip())
                
            # Amount (Col 7)
            if row[debitCreditIndex] and str(row[debitCreditIndex]).strip():
                merged_amt.append(str(row[debitCreditIndex]).strip())
                
            # Balance (Col 8)
            if row[balanceIndex] and str(row[balanceIndex]).strip():
                merged_bal.append(str(row[balanceIndex]).strip())
        
        # Join strategies
        # Date: Space joined (e.g., "01 Jun 2025 11:20 AM")
        final_date = " ".join(merged_date)
        
        # Description: Joined without separator based on "Payment from" example reconstruction
        # User example: "UPI/SHIVAMCLINIC..."
        final_desc = "".join(merged_desc)
        
        # Ref: Joined without separator (usually single line, but simple concatenation is safest for split IDs)
        final_ref = "".join(merged_ref)
        
        # Amount: Joined without separator
        final_amt = "".join(merged_amt)
        
        # Balance: Joined without separator
        final_bal = "".join(merged_bal)
        
        # Create single row for this transaction
        merged_transactions.append([
            final_date,
            final_desc,
            final_ref,
            final_amt,
            final_bal
        ])
        
    return merged_transactions

