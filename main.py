import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

st.title("Nova AI")

with st.sidebar:
    st.header("Upload options")
    
    # Paste content area
    st.subheader("Paste Content")
    pasted_content = st.text_area(
        "Paste anything here",
        placeholder="Paste text, code, or any content you want Nova to analyze",
        height=150,
        key="paste_area"
    )
    
    # File uploader
    st.subheader("Upload Files")
    uploaded_files = st.file_uploader(
        "Add files for Nova to read",
        accept_multiple_files=True,
        type=['txt', 'py', 'js', 'json', 'csv', 'md', 'pdf', 'docx']
    )

GROQ_KEY = os.getenv("GROQ_API_KEY")

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

user_query = st.chat_input("Send Nova a message")

# Handle pasted content and files
if uploaded_files or pasted_content:
    col1, col2 = st.columns(2)
    
    with col1:
        send_files_btn = st.button("📎 Send Files & Content", use_container_width=True)
    with col2:
        clear_btn = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_btn:
        st.session_state.pop("paste_area", None)
        st.rerun()
    
    if send_files_btn:
        # Build the message with files and pasted content
        message_parts = []
        
        if pasted_content:
            message_parts.append(f"**Pasted Content:**\n{pasted_content}")
        
        if uploaded_files:
            message_parts.append("\n**Uploaded Files:**\n")
            for file in uploaded_files:
                file_content = read_file_content(file)
                message_parts.append(f"\n--- File: {file.name} ---\n{file_content}\n")
        
        full_message = "\n".join(message_parts)
        
        st.session_state.messages.append({"role": "user", "content": full_message})
        st.chat_message("user").write(full_message)

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are Nova, a helpful AI assistant."},
                    *st.session_state.messages
                ]
            )

            ai_reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            st.chat_message("assistant").write(ai_reply)

        except Exception as e:
            st.error(f"Error: {e}")
        
        st.rerun()

elif user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are Nova, a helpful AI assistant."},
                *st.session_state.messages
            ]
        )

        ai_reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        st.chat_message("assistant").write(ai_reply)

    except Exception as e:
        st.error(f"Error: {e}")
