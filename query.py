from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from pinecone import Pinecone
from dotenv import load_dotenv
import google.generativeai as genai

# Load API keys

load_dotenv()  # Load .env file

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("portfolio-setion-index")  # replace with your index name



# Initialize Flask
app = Flask(__name__)
CORS(app)

# Initialize Pinecone


# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# ---- Functions ----
def search_pinecone(query):
    """Search Pinecone for relevant portfolio data."""
    query_embedding = genai.embed_content(
        model="models/embedding-001",
        content=query
    )["embedding"]

    results = index.query(vector=query_embedding, top_k=3, include_metadata=True)
    return results

def ask_portfolio(question):
    """RAG: Search Pinecone + Ask Gemini"""
    matches = search_pinecone(question)

    context = "\n".join([m["metadata"]["text"] for m in matches["matches"]])
    prompt = f"""
    You are a portfolio assistant. Answer based on the context below.
    Context:
    {context}

    Question: {question}
    Answer:
    """
    response = model.generate_content(prompt)
    return response.text

# ---- API Endpoint ----
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    query = data.get("query", "")
    if not query:
        return jsonify({"answer": "Please provide a query"}), 400

    answer = ask_portfolio(query)
    return jsonify({"answer": answer})

# ---- Run ----
if __name__ == "__main__":
    app.run(debug=True)
