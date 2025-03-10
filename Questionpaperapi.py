from Questionpaper import QuestionPaperPipeline
from fastapi import FastAPI, UploadFile, File
from typing import List
import shutil
import os
import json

app = FastAPI()


@app.post("/process_pdfs/")
async def process_pdfs(files: List[UploadFile] = File(...)):
    """API endpoint to process PDF files and return a JSON response."""
    file_paths = []

    # Save uploaded files temporarily
    for file in files:
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_paths.append(file_path)

    # Run the Question Paper Pipeline
    pipeline = QuestionPaperPipeline(file_paths)
    json_output = pipeline.run_pipeline()

    # Remove temporary files
    for path in file_paths:
        os.remove(path)

    return json.loads(json_output)  # Return JSON response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
