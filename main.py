import kotakBank
import sys
import pdfplumber
import json

def _process_single_page(pdf_path, page_num, bank_name, password):
    """
    Worker function for ProcessPoolExecutor.
    Each process opens the PDF independently to avoid thread/process safety issues.
    """
    import pdfplumber
    import traceback
    
    try:
        # Re-import logic based on bank_name inside the process
        match bank_name:
            case "UNION BANK OF INDIA":
                from unionBank.grouping_logic import group_transactions
                from unionBank.table_settings import table_settings
            case "HDFC BANK":
                from hdfcBank.grouping_logic import group_transactions
                from hdfcBank.table_settings import table_settings
            case "ICICI BANK":
                from iciciBank.grouping_logic import group_transactions
                from iciciBank.table_settings import table_settings
            case "KARNAVATI BANK":
                from karnavatiBank.grouping_logic import group_transactions
                from karnavatiBank.table_settings import table_settings
            case "KOTAK MAHINDRA BANK" | _:
                from kotakBank.grouping_logic import group_transactions
                from kotakBank.table_settings import table_settings

        with pdfplumber.open(pdf_path, password=password) as pdf:
            page = pdf.pages[page_num - 1]
            print(f"Processing page {page_num} in process...")
            tables = page.extract_tables(table_settings)
            return group_transactions(tables, page_num)
            
    except Exception as e:
        print(f"❌ Error on page {page_num} in process: {e}")
        traceback.print_exc()
        return []

def process_bank_statement_pdf(pdf_file, bank_name="UNION BANK OF INDIA", password=None):
    """
    Process PDF using pdfplumber and the specified bank parser.
    Uses ProcessPoolExecutor for parallel processing and isolation.
    Yields results page-by-page.
    """
    from concurrent.futures import ProcessPoolExecutor
    
    # We need to import the parser components for the main process
    match bank_name:
        case "UNION BANK OF INDIA":
            from unionBank.structured_output import generate_structured_output
            from unionBank.grouping_logic import group_transactions
            from unionBank.table_settings import table_settings
        case "HDFC BANK":
            from hdfcBank.structured_output import generate_structured_output
            from hdfcBank.grouping_logic import group_transactions
            from hdfcBank.table_settings import table_settings
        case "ICICI BANK":
            from iciciBank.structured_output import generate_structured_output
            from iciciBank.grouping_logic import group_transactions
            from iciciBank.table_settings import table_settings
        case "KARNAVATI BANK":
            from karnavatiBank.structured_output import generate_structured_output
            from karnavatiBank.grouping_logic import group_transactions
            from karnavatiBank.table_settings import table_settings
        case "KOTAK MAHINDRA BANK" | _:
            from kotakBank.structured_output import generate_structured_output
            from kotakBank.grouping_logic import group_transactions
            from kotakBank.table_settings import table_settings

    # Process pages sequentially for memory stability on hosted environments (like Render)
    try:
        with pdfplumber.open(pdf_file, password=password) as pdf:
            page_count = len(pdf.pages)
            
            for i in range(page_count):
                page_num = i + 1
                try:
                    print(f"📦 Processing page {page_num}/{page_count}...")
                    page = pdf.pages[i]
                    
                    # Extract tables using settings
                    tables = page.extract_tables(table_settings)
                    # Group transactions using bank-specific logic
                    grouped_txns = group_transactions(tables, page_num)
                    
                    if grouped_txns:
                        page_txns = generate_structured_output(grouped_txns)
                        yield {
                            "page": page_num,
                            "transactions": page_txns
                        }
                    else:
                        yield {
                            "page": page_num,
                            "transactions": []
                        }
                except Exception as e:
                    print(f"❌ Error on page {page_num}: {e}")
                    yield {
                        "page": page_num,
                        "error": str(e),
                        "transactions": []
                    }
    except Exception as e:
        print(f"❌ Failed to open PDF: {e}")
        yield {
            "page": 0,
            "error": f"Failed to open PDF: {str(e)}",
            "transactions": []
        }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py <pdf_path> <output_path>")
    else:
        # Simple CLI wrapper
        txns = process_bank_statement_pdf(sys.argv[1])
        # with open(sys.argv[2], 'w') as f:
        #     json.dump(txns, f, indent=4)
