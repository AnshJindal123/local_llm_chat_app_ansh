
# Local LLM Chat Application

**Author:** Ansh Jindal  
**Repository:** [local_llm_chat_app_ansh](https://github.com/AnshJindal123/local_llm_chat_app_ansh)

---

## 1. Project Overview

This full-stack web application integrates a local Large Language Model (LLM) using **LM Studio**, enabling contextual and memory-aware chat functionalities.

Key technologies include:
- FAISS for fast vector search of embeddings
- Sentence Transformers for encoding messages
- MongoDB for session-based memory storage
- React frontend with file upload & chat UI

Users can chat with the LLM, upload `.txt` files to provide additional context, and reset memory with one click.

---

## 2. Features

-  **Contextual Chat**: Uses local LLM via LM Studio
-  **Vector Memory**: Embeddings retrieved via FAISS (384-d vectors)
-  **Text File Upload**: Allows long context ingestion (.txt only)
-  **Session-based Memory**: User ID stored with UUID in `localStorage`
-  **MongoDB Integration**: Stores per-session messages
-  **Reset Button**: Clears backend memory via a REST endpoint

---

##  3. Tech Stack

| Layer     | Technology                    |
|-----------|-------------------------------|
| Frontend  | React (Vite)                  |
| Backend   | FastAPI                       |
| LLM       | LM Studio (e.g. LLaMA 3)      |
| Embedding | all-MiniLM-L6-v2 (384-dim)    |
| Storage   | MongoDB (Motor) + FAISS       |

---

##  4. Setup Instructions

###  Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Ensure **LM Studio** is running on: `http://localhost:1234`

###  Frontend (React)

```bash
cd frontend
npm install
npm run start
```

---

##  5. Testing Instructions

- Upload a `.txt` file to populate vector memory
- Ask questions that reference the uploaded content
- Use the chat UI to engage in multi-turn conversations
- Press the **Reset Memory** button to clear backend memory
- Provide many sentences to test context and ask a random question from a sentence

---

## 6. System Flow (Conceptual)

```text
User Message → FAISS Context Retrieval → LM Studio Prompt → Response → MongoDB (store)
File Upload → Chunk Text → Vectorize → FAISS Store → Used as Context in Future Chats
```

---

##  7. Reset & Cleanup

Click the **Reset Memory** button on the UI to:
- Clear FAISS index (in-memory)
- Delete session history from MongoDB

This ensures the next interaction starts with a clean slate.

---

##  8. Sample `.env` (for backend)

```
MONGODB_URI=mongodb://localhost:27017
DB_NAME=llmchat
```

##  Final Note

This project demonstrates how powerful local LLMs can be when paired with real-time vector search, memory handling, and clean UI design.

