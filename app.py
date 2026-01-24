import streamlit as st
import google.generativeai as genai

# 1. Page Configuration
st.set_page_config(page_title="y1", layout="centered")

st.markdown("""
    <style>
    .stMarkdown { text-align: right; }
    div[data-testid="stVerticalBlock"] { direction: rtl; }
    div[data-testid="stChatInput"] { direction: ltr; }
    </style>
    """, unsafe_allow_html=True)

st.title("y1")

# 2. API Configuration
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API Key Missing")
    st.stop()

# 3. Forced Stable Path (The fix for Iraq 404/429 issues)
# We use the explicit versioned string to bypass the 404 error
try:
    model = genai.GenerativeModel('models/gemini-1.5-flash-001')
except:
    model = genai.GenerativeModel('gemini-pro')

# 4. Session State Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Chat Engine
if prompt := st.chat_input("Enter message"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            history = [
                {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                for m in st.session_state.messages[:-1]
            ]
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Status: {str(e)}")
