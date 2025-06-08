from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import process_input
import tempfile

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserQuery(BaseModel):
    text: str
    session_id: str = "default"

@app.post("/chat")
async def chat_endpoint(query: UserQuery):
    try:
        response = process_input(query.text)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), session_id: str = "default"):
    try:
        print(f"Received file: {file.filename}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        print(f"Saved temp file to: {tmp_path}")

        # Pass to PDF processor
        result = process_input(f"ADD_PDF {tmp_path}")
        print(f"Processing result: {result}")

        return {"status": result}
    except Exception as e:
        print(f"Upload error: {str(e)}")  # Log the actual error
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    return {"status": "healthy"}