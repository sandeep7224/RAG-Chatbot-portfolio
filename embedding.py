from pinecone import Pinecone, ServerlessSpec
import google.generativeai as genai
import json
import os

# Load env variables
PINECONE_API_KEY = "pcsk_3Qr8TR_BwL2C9RE4skDwkWmMkKz4QJ8FW6FTjb14vba9Jvi7b6YhBKyKHqvX2tuUvhsMtG"
GOOGLE_API_KEY = "AIzaSyCUgS5kvYhNIRs2ExfXfifdBK7fpWSzDOc"

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create index if not exists
index_name = "portfolio-setion-index"

if index_name not in [i["name"] for i in pc.list_indexes()]:
    pc.create_index(
        name=index_name,
        dimension=768,  # Gemini embeddings are 768-dim
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

# Connect to the index
index = pc.Index(index_name)

# Function to create embeddings using Gemini
def get_embedding(text):
    model = "models/text-embedding-004"
    result = genai.embed_content(model=model, content=text)
    return result["embedding"]

# Load chunks from file (from Step 1 output)
with open("chunks.jsonl", "r", encoding="utf-8") as f:
    chunks = [json.loads(line) for line in f]

# Insert embeddings into Pinecone
vectors = []
for chunk in chunks:
    embedding = get_embedding(chunk["text"])
    vectors.append({
        "id": chunk["id"],
        "values": embedding,
        "metadata": chunk["metadata"] | {"text": chunk["text"]}
    })

# Upsert to Pinecone
index.upsert(vectors=vectors)

print("✅ Portfolio data stored in Pinecone successfully!")










