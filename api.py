import os
import shutil
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException, Depends
from dotenv import load_dotenv
import pdfplumber
from main import process_bank_statement_pdf

from config import config

app = FastAPI()

# API Key from configuration
API_KEY = config.API_KEY

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

@app.post("/parse")
async def parse_bank_statement(
    file: UploadFile = File(...),
    bank_name: str = Form("UNION BANK OF INDIA"),
    password: Optional[str] = Form(None),
    x_api_key: str = Depends(verify_api_key)
):
    try:
        # Save temp file
        temp_filename = f"temp_{file.filename}"
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        try:
            # Determine bank name constant if needed, or pass string directly as main.py expects string
            # main.process_bank_statement_pdf expects the string name
            
            # Get Page Count
            page_count = 0
            try:
                with pdfplumber.open(temp_filename, password=password) as pdf:
                    page_count = len(pdf.pages)
            except Exception as e:
                print(f"Error reading page count: {e}")

            transactions = process_bank_statement_pdf(temp_filename, bank_name=bank_name, password=password)
            
            return {
                "status": "success",
                "bank": bank_name,
                "transactions": transactions,
                "documentmetadata": {
                    "filename": file.filename,
                    "page_count": page_count,
                }
            }
        finally:
            # Cleanup
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
