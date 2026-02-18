import streamlit as st
import os
import sys
import uuid
from gtts import gTTS

# ---------------- PATH ---------------- #

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# ---------------- IMPORTS ---------------- #

from backend.db import init_db, save_chat, load_chats
from backend.auth import login, register
from backend.rag_engine import ask_question


# ---------------- INIT DB ---------------- #

init_db()


# ---------------- SESSION ---------------- #

if "user" not in st.session_state:
    st.session_state.user = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    st.session_state.history = []


# ---------------- LOGIN ---------------- #

if st.session_state.user is None:

    st.set_page_config("Login", "🔐")

    st.title("🔐 Login System")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:

        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):

            if login(u, p):

                st.session_state.user = u
                st.rerun()

            else:
                st.error("Invalid username or password")


    with tab2:

        ru = st.text_input("New Username")
        rp = st.text_input("New Password", type="password")

        if st.button("Register"):

            if register(ru, rp):

                st.success("Registered successfully! Login now.")

            else:
                st.error("Username already exists")

    st.stop()


# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="RAG AI Assistant",
    page_icon="🤖",
    layout="wide"
)


# ---------------- LOAD HISTORY ---------------- #

if len(st.session_state.messages) == 0:

    chats = load_chats(st.session_state.user)

    for q, a in chats:

        st.session_state.messages.append(
            {"role": "user", "content": q}
        )

        st.session_state.messages.append(
            {"role": "assistant", "content": a}
        )

        st.session_state.history.append({
            "question": q,
            "answer": a
        })


# ---------------- SIDEBAR ---------------- #

st.sidebar.title("⚙ Settings")


# Theme
theme = st.sidebar.radio(
    "Theme Mode",
    ["🌙 Dark", "☀️ Light"]
)


# Light Mode
if theme == "☀️ Light":

    st.markdown(
        """
        <style>
        body, .stApp {
            background-color: white;
            color: black;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# Upload PDF
st.sidebar.markdown("### 📄 Upload PDF")

uploaded_file = st.sidebar.file_uploader(
    "Upload",
    type="pdf",
    label_visibility="collapsed"
)


if uploaded_file:

    path = os.path.join("data", uploaded_file.name)

    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.sidebar.success("✅ PDF Uploaded")


# ---------------- HISTORY PANEL ---------------- #

st.sidebar.markdown("---")
st.sidebar.markdown("## 📜 History")

if len(st.session_state.history) == 0:

    st.sidebar.info("No history yet")

else:

    for i, item in enumerate(st.session_state.history):

        with st.sidebar.expander(
            f"Q{i+1}: {item['question'][:30]}..."
        ):

            st.markdown("**Question:**")
            st.write(item["question"])

            st.markdown("**Answer:**")
            st.write(item["answer"])


# ---------------- MAIN UI ---------------- #

st.title("🤖 AI Document Assistant")


# Show Messages
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ---------------- INPUT ---------------- #

prompt = st.chat_input("Ask something about your document...")


if prompt:

    # User Message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })


    with st.chat_message("user"):
        st.markdown(prompt)


    # Assistant
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:
                response = ask_question(prompt)

            except Exception as e:

                response = f"❌ Error: {str(e)}"


        # Answer Box
        st.markdown(
            f"""
            <div style="
                background:#1f2937;
                padding:15px;
                border-radius:10px;
                border:1px solid #374151;
                margin-bottom:10px;
            ">
            {response}
            </div>
            """,
            unsafe_allow_html=True
        )


        col1, col2 = st.columns(2)


        # Copy
        with col1:
            st.code(response)


        # Audio
        with col2:

            if st.button("🔊 Play Audio", key=str(uuid.uuid4())):

                try:

                    tts = gTTS(response)

                    filename = f"audio_{uuid.uuid4()}.mp3"

                    tts.save(filename)

                    with open(filename, "rb") as audio:

                        st.audio(audio.read(), format="audio/mp3")

                except:

                    st.error("Audio failed")


    # Save Assistant Message
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })


    # Save DB
    save_chat(
        st.session_state.user,
        prompt,
        response
    )


    # Save Sidebar History
    st.session_state.history.append({
        "question": prompt,
        "answer": response
    })
