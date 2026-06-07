import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

st.title("Nova AI")

with st.sidebar:
    st.header("App Settings")

GROQ_KEY = os.getenv("GROQ_API_KEY")

SYSTEM_PROMPT = """You are Nova, an AI assistant.
Use only the user's message and any attached file contents to answer.
Do not hallucinate or invent details.
If the requested information is not available, say you don't know and ask for clarification.
Be accurate, concise, and grounded in the provided content.
"""

client = OpenAI(
    api_key=GROQ_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to read file contents
def read_file_content(uploaded_file):
    try:
        if uploaded_file.type == "application/pdf":
            # For PDF, we'd need PyPDF2 or similar
            return f"[PDF file: {uploaded_file.name} - PDF reading requires additional libraries]"
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # For DOCX, we'd need python-docx
            return f"[DOCX file: {uploaded_file.name} - DOCX reading requires additional libraries]"
        else:
            return uploaded_file.read().decode("utf-8")
    except Exception as e:
        return f"[Error reading file {uploaded_file.name}: {str(e)}]"

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Unified chat form: type/paste in the box and drag/drop files into the uploader
st.markdown("---")

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Submission callback reads widgets from session_state to avoid mutating after widget creation
def submit_message():
    user_query = st.session_state.get("user_input", "").strip()
    if not user_query:
        return

    message_parts = [user_query]

    uploaded = st.session_state.get("uploaded_files")
    if uploaded:
        message_parts.append("\n**Attached Files:**\n")
        for file in uploaded:
            file_content = read_file_content(file)
            message_parts.append(f"\n--- File: {file.name} ---\n{file_content}\n")

    full_message = "".join(message_parts)
    st.session_state.messages.append({"role": "user", "content": full_message})
    st.chat_message("user").write(full_message)

    # Clear the input safely
    st.session_state["user_input"] = ""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *st.session_state.messages],
        )

        ai_reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        st.chat_message("assistant").write(ai_reply)

    except Exception as e:
        st.error(f"Error: {e}")

with st.form("nova_form"):
    st.write("Type or paste your message below, then attach files if needed.")
    st.text_area(
        "Your message to Nova",
        key="user_input",
        placeholder="Type or paste text here",
        height=180,
    )
    st.file_uploader(
        "Attach files (drag and drop supported)",
        accept_multiple_files=True,
        type=["txt", "py", "js", "json", "csv", "md", "pdf", "docx"],
        key="uploaded_files",
    )
    st.form_submit_button("Send Nova message", on_click=submit_message)
