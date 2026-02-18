import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "embeddings")


def ingest_docs():

    docs = []

    for file in os.listdir(DATA_PATH):

        if file.endswith(".pdf"):

            path = os.path.join(DATA_PATH, file)

            print("📄 Loading:", file)

            loader = PyPDFLoader(path)

            docs.extend(loader.load())


    if not docs:
        print("❌ No PDFs found")
        return


    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=80
    )

    chunks = splitter.split_documents(docs)

    print("✂️ Chunks:", len(chunks))


    embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    cache_folder="models"
)



    print("🧠 Creating embeddings...")

    db = FAISS.from_documents(chunks, embeddings)

    db.save_local(DB_PATH)

    print("✅ Ingestion complete!")


if __name__ == "__main__":
    ingest_docs()
