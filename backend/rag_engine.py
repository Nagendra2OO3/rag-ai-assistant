import os
from dotenv import load_dotenv
import streamlit as st

from groq import Groq

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


# Load env
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise Exception("❌ GROQ_API_KEY missing")

print("✅ Groq API Loaded")

client = Groq(api_key=API_KEY)


# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "embeddings")


# ---------------- CACHE EMBEDDINGS ---------------- #

@st.cache_resource
def load_embeddings():

    return HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)



# ---------------- CACHE VECTOR DB ---------------- #

@st.cache_resource
def load_db():

    embeddings = load_embeddings()

    return FAISS.load_local(
        DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )


# ---------------- CACHE LLM CLIENT ---------------- #

@st.cache_resource
def load_client():

    return Groq(api_key=API_KEY)


# ---------------- MAIN QA FUNCTION ---------------- #

def ask_question(query):

    db = load_db()
    client = load_client()

    # Search
    docs = db.similarity_search(query, k=3)

    if not docs:
        return "❌ No relevant content found in document."

    context = "\n".join([d.page_content for d in docs])

    prompt = f"""
Answer only from this context.

Context:
{context}

Question:
{query}

Answer:
"""

    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],

        temperature=0.3,
        max_tokens=400
    )

    return response.choices[0].message.content


# ---------------- TERMINAL TEST ---------------- #

if __name__ == "__main__":

    while True:

        q = input("\nAsk: ")

        if q.lower() == "exit":
            break

        print("\nAnswer:\n", ask_question(q))
