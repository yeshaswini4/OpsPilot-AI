# 🚀 OpsPilot AI

![React](https://img.shields.io/badge/React-18-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Gemini](https://img.shields.io/badge/Google-Gemini-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

**AI-Powered Document Intelligence Assistant**

OpsPilot AI is a Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents and ask natural language questions. The system retrieves relevant document content using ChromaDB vector search and generates context-aware answers with Google's Gemini AI.

---

## 📖 Overview

OpsPilot AI simplifies document understanding by combining semantic search with large language models. Instead of manually searching through long PDFs, users can upload a document and instantly ask questions in natural language.

---

## ✨ Features

- 📄 Upload PDF documents
- 🔍 Automatic text extraction
- ✂️ Intelligent text chunking
- 🧠 Vector embeddings using Sentence Transformers
- 📚 ChromaDB vector database
- 🤖 AI-powered question answering using Gemini
- 💬 ChatGPT-style chat interface
- 🌙 Modern dark theme UI
- 📱 Responsive design
- ⚡ FastAPI backend
- ⚛️ React frontend

---

## 🛠 Tech Stack

### Frontend
- React
- Vite
- Axios
- React Icons
- CSS

### Backend
- FastAPI
- Python

### AI
- Google Gemini 2.5 Flash
- Sentence Transformers (MiniLM-L6-v2)

### Database
- ChromaDB

### PDF Processing
- pypdf
- langchain-text-splitters

---

## 🏗 Architecture

```text
React Frontend
       │
       ▼
Axios API
       │
       ▼
FastAPI Backend
       │
       ▼
PDF Upload
       │
       ▼
Text Extraction
       │
       ▼
Chunking
       │
       ▼
Sentence Embeddings
       │
       ▼
ChromaDB
       │
       ▼
Relevant Context Retrieval
       │
       ▼
Gemini AI
       │
       ▼
Response
       │
       ▼
React Chat Interface
```

---

## 📂 Project Structure

```
OpsPilot-AI/
│
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── upload.py
│   │   │   └── chat.py
│   │   ├── services/
│   │   │   ├── pdf_service.py
│   │   │   ├── chunk_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── vector_service.py
│   │   │   └── llm_service.py
│   │   ├── models/
│   │   │   └── schemas.py
│   │   ├── utils/
│   │   │   └── helpers.py
│   │   ├── main.py
│   │   └── config.py
│   ├── uploads/
│   ├── vector_db/
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── UploadBox.jsx
│   │   │   ├── ChatBox.jsx
│   │   │   ├── Message.jsx
│   │   │   ├── InputBox.jsx
│   │   │   ├── Loader.jsx
│   │   │   ├── Toast.jsx
│   │   │   └── DocumentCard.jsx
│   │   ├── pages/
│   │   │   └── Home.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── .env.example
│   └── package.json
│
├── screenshots/
├── README.md
└── LICENSE
```

---

## 🚀 Installation

### Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/OpsPilot-AI.git
cd OpsPilot-AI
```

---

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

Create `.env` from `.env.example`:

```
GEMINI_API_KEY=your_gemini_api_key
UPLOAD_FOLDER=uploads
VECTOR_DB_PATH=vector_db
```

Run:

```bash
uvicorn app.main:app --reload
```

Backend runs on: `http://127.0.0.1:8000`

API docs: `http://127.0.0.1:8000/docs`

---

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Create `.env` from `.env.example`:

```
VITE_API_URL=http://127.0.0.1:8000
```

Frontend runs on: `http://localhost:5173`

---

## 🔑 Environment Variables

### Backend `.env`

| Variable         | Description                  |
|------------------|------------------------------|
| GEMINI_API_KEY   | Google Gemini API key        |
| UPLOAD_FOLDER    | Folder to store uploaded PDFs|
| VECTOR_DB_PATH   | Path for ChromaDB storage    |

### Frontend `.env`

| Variable       | Description          |
|----------------|----------------------|
| VITE_API_URL   | Backend API base URL |

---

## 📡 API Endpoints

| Method | Endpoint     | Description             |
|--------|--------------|-------------------------|
| GET    | /            | Health check            |
| GET    | /health      | Server status           |
| POST   | /upload      | Upload PDF              |
| POST   | /chat        | Ask a question          |
| GET    | /documents   | List uploaded documents |

### Upload PDF

```
POST /upload
Content-Type: multipart/form-data

file: <pdf_file>
```

### Ask Question

```
POST /chat
Content-Type: application/json

{
  "question": "What is the penalty clause?"
}
```

---

## 📸 Screenshots

### Home
![Home](screenshots/home.png)

### Upload
![Upload](screenshots/upload.png)

### Chat
![Chat](screenshots/chat.png)

---

## 🎯 Future Improvements

- Multi-document chat
- User authentication
- Conversation history
- Source page references
- OCR support
- Docker deployment
- Cloud storage
- Role-based access

---

## 🌐 Live Demo

Frontend: `https://your-vercel-app.vercel.app`

Backend API: `https://your-render-app.onrender.com`

---

## 👩‍💻 Author

**Yeshaswini G**

MCA Graduate | Python Full-Stack Developer

- GitHub: [https://github.com/YOUR_USERNAME](https://github.com/YOUR_USERNAME)
- LinkedIn: [https://linkedin.com/in/YOUR_PROFILE](https://linkedin.com/in/YOUR_PROFILE)

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.
