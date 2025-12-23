import os
import requests
import streamlit as st
from datetime import datetime

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="MT Coffee Chatbot", page_icon="☕")

st.title("☕ MT Coffee Chatbot")

# =============================== SESSION STATE ================================
if "session_id" not in st.session_state:
  st.session_state.session_id = None

if "messages" not in st.session_state:
  st.session_state.messages = []

# ============================= START CHAT SESSION =============================
def start_chat():
  res = requests.post(
    f"{API_BASE_URL}/chat/start",
    json={"customer_id": None}
  )
  data = res.json()
  st.session_state.session_id = data["session_id"]

  # Add welcome message
  st.session_state.messages.append({
    "role": "assistant",
    "content": data["message"]
  })

if st.session_state.session_id is None:
  start_chat()

# ================================ DISPLAY CHAT ================================
for msg in st.session_state.messages:
  with st.chat_message(msg["role"]):
    st.markdown(msg["content"])

# ================================= USER INPUT =================================
user_input = st.chat_input("Bạn muốn uống gì hôm nay nhỉ?...")

if user_input:
  # Show user message
  st.session_state.messages.append({
    "role": "user",
    "content": user_input
  })

  with st.chat_message("user"):
    st.markdown(user_input)

  # Call backend
  payload = {
    "session_id": st.session_state.session_id,
    "message": user_input
  }

  with st.chat_message("assistant"):
    with st.spinner("Đang trả lời..."):
      res = requests.post(
        f"{API_BASE_URL}/chat/message",
        json=payload,
      )
      data = res.json()
      answer = data["message"]
      st.markdown(answer)

  st.session_state.messages.append({
    "role": "assistant",
    "content": answer
  })


