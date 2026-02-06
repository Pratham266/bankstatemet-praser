import os
import shutil
import uuid
import json
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException, Depends
from fastapi.responses import FileResponse
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

# Ensure results directory exists
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

@app.post("/parse")
async def parse_bank_statement(
    file: UploadFile = File(...),
    bank_name: str = Form("UNION BANK OF INDIA"),
    password: Optional[str] = Form(None),
    x_api_key: str = Depends(verify_api_key)
):
    try:
        # Save temp file
        temp_filename = f"temp_{uuid.uuid4()}_{file.filename}"
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        try:
            # Get Page Count
            page_count = 0
            try:
                with pdfplumber.open(temp_filename, password=password) as pdf:
                    page_count = len(pdf.pages)
            except Exception as e:
                print(f"Error reading page count: {e}")

            transactions = process_bank_statement_pdf(temp_filename, bank_name=bank_name, password=password)
            
            # Create result object
            result_data = {
                "status": "success",
                "bank": bank_name,
                "transactions": transactions,
                "documentmetadata": {
                    "filename": file.filename,
                    "page_count": page_count,
                }
            }
            
            # Save result to a unique JSON file
            result_id = str(uuid.uuid4())
            result_filename = f"{result_id}.json"
            result_path = os.path.join(RESULTS_DIR, result_filename)
            
            with open(result_path, "w") as f:
                json.dump(result_data, f)
            
            return {
                "status": "success",
                "file_id": result_id
            }
        finally:
            # Cleanup temp PDF
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@app.get("/results/{file_id}")
async def get_result_file(file_id: str, x_api_key: str = Depends(verify_api_key)):
    result_path = os.path.join(RESULTS_DIR, f"{file_id}.json")
    if not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="Result file not found")
    return FileResponse(result_path)

@app.delete("/results/{file_id}")
async def delete_result_file(file_id: str, x_api_key: str = Depends(verify_api_key)):
    result_path = os.path.join(RESULTS_DIR, f"{file_id}.json")
    if os.path.exists(result_path):
        os.remove(result_path)
        return {"status": "success", "message": "Result file deleted"}
    raise HTTPException(status_code=404, detail="Result file not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
