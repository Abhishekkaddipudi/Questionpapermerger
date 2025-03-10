# FastAPI Question Paper Processing API

This is a FastAPI-based web service that processes PDF files containing question papers. It extracts questions, clusters them using K-Means, and returns a structured JSON output.

## Features
- Extracts text from PDFs
- Uses regex to extract questions
- Clusters questions using TF-IDF and K-Means
- Selects final questions for a question paper
- Returns structured JSON output
- Supports multiple PDF uploads via API

---

## Installation and Setup (Run Locally)

### **1. Clone the Repository**
```sh
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### **2. Create and Activate a Virtual Environment**
#### **On Windows:**
```sh
python -m venv venv
venv\Scripts\activate
```

#### **On macOS/Linux:**
```sh
python3 -m venv venv
source venv/bin/activate
```

### **3. Install Dependencies**
```sh
pip install -r requirements.txt
```

### **4. Run the API Server**
```sh
uvicorn questionpaperapi:app --host 0.0.0.0 --port 8000 --reload
```
#### OR
```python
python questionpaperapi.py
```

### **5. Test API Endpoints**
Once the server is running, you can access the interactive Swagger UI at:
```
http://127.0.0.1:8000/docs
```

To manually test using `cURL`:
```sh
curl -X 'POST' \
  'http://127.0.0.1:8000/process_pdfs/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'files=@yourfile.pdf'
```


---

## Author
Developed by [Abhishek Kaddipudi](https://github.com/Abhishekkaddipudi).

