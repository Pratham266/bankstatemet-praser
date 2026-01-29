import kotakBank
import sys
import pdfplumber
import json

def process_bank_statement_pdf(pdf_file, bank_name="UNION BANK OF INDIA", password=None):
    """
    Process PDF using pdfplumber (text-based) and the specified bank parser.
    Returns a list of structured transaction dictionaries.
    """
    
    match bank_name:
        case "UNION BANK OF INDIA":
            from unionBank.grouping_logic import group_transactions
            from unionBank.structured_output import generate_structured_output
            from unionBank.table_settings import table_settings
        case "HDFC BANK":
            from hdfcBank.grouping_logic import group_transactions
            from hdfcBank.structured_output import generate_structured_output
            from hdfcBank.table_settings import table_settings
        case "ICICI BANK":
            from iciciBank.grouping_logic import group_transactions
            from iciciBank.structured_output import generate_structured_output
            from iciciBank.table_settings import table_settings
        case "KOTAK MAHINDRA BANK":
            # Default to Kotak (or explicitly check "KOTAK MAHINDRA BANK")
            from kotakBank.grouping_logic import group_transactions
            from kotakBank.structured_output import generate_structured_output
            from kotakBank.table_settings import table_settings
        case _:
            # Default to Kotak (or explicitly check "KOTAK MAHINDRA BANK")
            from kotakBank.grouping_logic import group_transactions
            from kotakBank.structured_output import generate_structured_output
            from kotakBank.table_settings import table_settings

    all_transactions = []

    # pdf_file can be a path or a file-like object (bytes)
    with pdfplumber.open(pdf_file, password=password) as pdf:
        for i, page in enumerate(pdf.pages):
            print(f"Processing page {i+1} with pdfplumber...")
            tables = page.extract_tables(table_settings)
            with open(f"page_{i+1}_raw1.json", "w") as f:
                json.dump(tables, f, indent=4)
            # Group transactions
            grouped_txns = group_transactions(tables,i+1)

            with open(f"page_{i+1}_raw3.json", "w") as f:
                json.dump(grouped_txns, f, indent=4)

            # Generate structured output
            page_txns = generate_structured_output(grouped_txns)
            all_transactions.extend(page_txns)
            
            with open(f"page_{i+1}_raw4.json", "w") as f:
                json.dump(page_txns, f, indent=4)
            
    return all_transactions

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py <pdf_path> <output_path>")
    else:
        # Simple CLI wrapper
        txns = process_bank_statement_pdf(sys.argv[1])
        with open(sys.argv[2], 'w') as f:
            json.dump(txns, f, indent=4)
