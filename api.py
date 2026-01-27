from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException, Depends
from typing import Optional
import shutil
import os
from main import process_bank_statement_pdf

app = FastAPI()

# Simple API Key Validation
API_KEY = "1234567890"  # Ideally handled via environment variables

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
            
            transactions = process_bank_statement_pdf(temp_filename, bank_name=bank_name, password=password)
            
            return {
                "status": "success",
                "bank": bank_name,
                "transactions": transactions
            }
        finally:
            # Cleanup
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
