import streamlit as st
import google.generativeai as genai

# 1. UI Configuration (Clean & Organized)
st.set_page_config(page_title="y1", layout="centered")

# Arabic Layout (RTL) Support
st.markdown("""
    <style>
    .stMarkdown { text-align: right; }
    div[data-testid="stVerticalBlock"] { direction: rtl; }
    div[data-testid="stChatInput"] { direction: ltr; }
    </style>
    """, unsafe_allow_html=True)

st.title("y1")

# 2. Authentication
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API Key Missing")
    st.stop()

# 3. Smart Model Discovery (The logic that found 2.5-flash in Iraq)
@st.cache_resource
def discover_model():
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if available:
            # Picking the first active model recognized by the local server
            return genai.GenerativeModel(available[0]), available[0]
        return None, None
    except Exception:
        return None, None

model_engine, model_name = discover_model()

# 4. Session-Based Memory (Ephemeral - Clears on exit)
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. Core Interaction Engine
if prompt := st.chat_input("Enter message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Rebuilding chat history for the session
            history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                       for m in st.session_state.messages[:-1]]
            
            chat_session = model_engine.start_chat(history=history)
            response = chat_session.send_message(prompt)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"System Notification: {str(e)}")
