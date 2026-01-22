import json
import re

def is_date(text):
    return bool(
        text and re.search(r'\d{1,2}-\d{1,2}-\d{4}', text)
    )

def is_time(text):
    return bool(
        text and re.search(r'\d{1,2}:\d{2}\s*(AM|PM)', text)
    )

def is_transaction_start(row):
    """
    Transaction starts ONLY when a DATE is found in row[1].
    """
    if len(row) < 2:
        return False

    col1 = str(row[0]).strip()

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
    
    dateIndex=0
    transactionIdIndex=0
    remarksIndex=0
    amountIndex=0
    balanceIndex=0
    
    for page in pages:
        for row in page:
            if not row:
                continue
            row_upper = [str(c).upper().strip() for c in row]
            if len(row_upper) >= 2 and "BALANCE" in row_upper[-1] and "AMOUNT" in row_upper[-2]:
                for idx, val in enumerate(row):
                    if "DATE" in str(val).upper().strip():
                        dateIndex=idx
                    elif "SACTION ID" in str(val).upper().strip():
                        transactionIdIndex=idx
                    elif "REMARKS" in str(val).upper().strip():
                        remarksIndex=idx
                    elif "AMOUNT" in str(val).upper().strip():
                        amountIndex=idx
                    elif "BALANCE" in str(val).upper().strip():
                        balanceIndex=idx
                continue
            # Heuristic: New Transaction starts with a date in the first column
            if is_transaction_start(row):
                # If we were building a transaction, save it
                if current_transaction:
                    transactions.append(current_transaction)
                
                # Start new transaction
                current_transaction = [row]
            
    # Append the final transaction if exists
    if current_transaction:
        transactions.append(current_transaction)
    with open(f"page_{page_number}_raw2.json", "w") as f:
                json.dump(transactions, f, indent=4)
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

            if row[dateIndex] and str(row[dateIndex]).strip():
                merged_date.append(str(row[dateIndex]).strip())

            ref_combined = "".join(str(row[i]).strip() for i in range(transactionIdIndex, remarksIndex) if i < len(row) and row[i])
            if ref_combined:
                merged_ref.append(ref_combined)
            
            desc_combined = "".join(str(row[i]).strip() for i in range(remarksIndex, amountIndex) if i < len(row) and row[i])
            if desc_combined:
                merged_desc.append(desc_combined)
                
            if row[amountIndex] and str(row[amountIndex]).strip():
                merged_amt.append(str(row[amountIndex]).strip())
                
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
