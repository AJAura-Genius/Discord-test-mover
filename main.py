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

# File uploader in main area
st.markdown("---")
uploaded_files = st.file_uploader(
    "Attach files (optional)",
    accept_multiple_files=True,
    type=['txt', 'py', 'js', 'json', 'csv', 'md', 'pdf', 'docx']
)

# Chat input area that supports copy/paste
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

st.text_area(
    "Your message to Nova",
    value=st.session_state.user_input,
    key="user_input",
    placeholder="Type or paste text here, then press Send",
    height=140
)

if st.button("Send Nova message"):
    user_query = st.session_state.user_input.strip()
    if user_query:
        message_parts = [user_query]

        if uploaded_files:
            message_parts.append("\n**Attached Files:**\n")
            for file in uploaded_files:
                file_content = read_file_content(file)
                message_parts.append(f"\n--- File: {file.name} ---\n{file_content}\n")

        full_message = "".join(message_parts)
        st.session_state.messages.append({"role": "user", "content": full_message})
        st.chat_message("user").write(full_message)
        st.session_state.user_input = ""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                temperature=0,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *st.session_state.messages,
                ],
            )

            ai_reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            st.chat_message("assistant").write(ai_reply)

        except Exception as e:
            st.error(f"Error: {e}")
