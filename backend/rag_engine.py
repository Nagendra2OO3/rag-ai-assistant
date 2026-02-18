import os
from dotenv import load_dotenv

from groq import Groq

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    print("❌ GROQ_API_KEY missing")
    exit()

print("✅ Groq API Loaded")

client = Groq(api_key=API_KEY)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "embeddings")


def load_db():
    embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    cache_folder="models"
)

    return FAISS.load_local(
        DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )


def ask_question(query):

    db = load_db()

    docs = db.similarity_search(query, k=3)

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


if __name__ == "__main__":

    while True:

        q = input("\nAsk: ")

        if q.lower() == "exit":
            break

        print("\nAnswer:\n", ask_question(q))
