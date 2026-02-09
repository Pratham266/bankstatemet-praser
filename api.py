import os
import asyncio
import shutil
import uuid
import json
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException, Depends
from fastapi.responses import FileResponse, StreamingResponse
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
    # Save temp file
    temp_filename = f"temp_{uuid.uuid4()}_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    async def result_generator():
        try:
            # Get Page Count first
            page_count = 0
            try:
                with pdfplumber.open(temp_filename, password=password) as pdf:
                    page_count = len(pdf.pages)
            except Exception as e:
                print(f"Error reading page count: {e}")

            # Yield Metadata first
            metadata = {
                "type": "metadata",
                "status": "success",
                "bank": bank_name,
                "documentmetadata": {
                    "filename": file.filename,
                    "page_count": page_count,
                }
            }
            yield json.dumps(metadata) + "\n"

            # Yield transactions page-by-page
            for page_result in process_bank_statement_pdf(temp_filename, bank_name=bank_name, password=password):
                page_result["type"] = "page_data"
                yield json.dumps(page_result) + "\n"
                # Important: Allow heartbeats/other tasks to run during intensive parsing
                await asyncio.sleep(0.01)

        except Exception as e:
            yield json.dumps({"type": "error", "message": str(e)}) + "\n"
        finally:
            # Cleanup temp PDF
            if os.path.exists(temp_filename):
                try:
                    os.remove(temp_filename)
                    print(f"🗑️ Cleaned up temp file: {temp_filename}")
                except Exception as cleanup_err:
                    print(f"Error cleaning up: {cleanup_err}")

    return StreamingResponse(result_generator(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
