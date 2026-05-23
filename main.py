import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Streamlit UI
st.title("Workspace AI")

with st.sidebar:
    st.header("App Settings")

# User input
user_query = st.chat_input("Send Nova a message")

# Get API key from .env
GROQ_KEY = os.getenv("GROQ_API_KEY")

# Create Groq client
client = OpenAI(
    api_key=GROQ_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# Chat handling
if user_query:
    st.chat_message("user").write(user_query)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # You can change models
            messages=[
                {"role": "system", "content": "You are Nova, a helpful AI assistant."},
                {"role": "user", "content": user_query}
            ]
        )

        ai_reply = response.choices[0].message.content

        st.chat_message("assistant").write(ai_reply)

    except Exception as e:
        st.error(f"Error: {e}")