from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import httpx
import logging
import uuid
import os
import pickle
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load .env (for Mongo URI)
load_dotenv()

# MongoDB Setup
mongo_client = AsyncIOMotorClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = mongo_client["chat_db"]
messages_collection = db["messages"]

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS (allow all for now, restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vectorization setup
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
DIM = 384
FAISS_INDEX_PATH = "faiss_index.index"
TEXT_CHUNKS_PATH = "texts.pkl"

if os.path.exists(FAISS_INDEX_PATH):
    index = faiss.read_index(FAISS_INDEX_PATH)
    text_chunks = pickle.load(open(TEXT_CHUNKS_PATH, "rb"))
else:
    index = faiss.IndexFlatL2(DIM)
    text_chunks = []

# Helper functions
def embed(text: str):
    return embedding_model.encode([text])[0]

def add_to_store(text: str):
    vector = embed(text)
    index.add(np.array([vector], dtype=np.float32))
    text_chunks.append(text)
    faiss.write_index(index, FAISS_INDEX_PATH)
    pickle.dump(text_chunks, open(TEXT_CHUNKS_PATH, "wb"))

def get_relevant_context(query: str, k=3):
    if index.ntotal == 0:
        return []
    vector = embed(query)
    D, I = index.search(np.array([vector], dtype=np.float32), k)
    return [text_chunks[i] for i in I[0] if i < len(text_chunks)]

# Chat request model
class ChatRequest(BaseModel):
    session_id: str
    message: str

# POST /chat route
@app.post("/chat/")
async def chat(chat_request: ChatRequest):
    try:
        session_id = chat_request.session_id
        user_msg = chat_request.message
        logger.info(f"Session {session_id} - user: {user_msg}")

        # Retrieve past messages for session
        past = await messages_collection.find({"session_id": session_id}).to_list(None)
        history = [{"role": "user", "content": m["message"]} for m in past]
        history.append({"role": "user", "content": user_msg})

        # Vector-based context
        relevant_chunks = get_relevant_context(user_msg, k=3)
        context = "\n---\n".join(relevant_chunks)

        # Build messages for LM
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Use the context below if needed."},
            {"role": "user", "content": context},
        ] + history

        # Call LM Studio
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:1234/v1/chat/completions",
                json={"model": "llama-3.2-1b-instruct.Q4_K_M", "messages": messages, "temperature": 0.7},
            )
            response.raise_for_status()
            reply = response.json()["choices"][0]["message"]["content"]

        # Save new message
        await messages_collection.insert_one({
            "session_id": session_id,
            "message": user_msg
        })

        return {"response": reply}

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Chat failed")

@app.post("/reset/")
def reset_system():
    global index, text_chunks
    index = faiss.IndexFlatL2(384)
    text_chunks.clear()
    return {"detail": "FAISS and memory reset"}


# Upload .txt file and vectorize
@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are allowed.")

    try:
        contents = (await file.read()).decode("utf-8")
        chunks = contents.split("\n\n")  # simple chunking
        for chunk in chunks:
            if chunk.strip():
                add_to_store(chunk.strip())
        return {"detail": f"{len(chunks)} chunks added from {file.filename}"}
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process file")
