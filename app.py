import streamlit as st
import google.generativeai as genai

# 1. Page Configuration
st.set_page_config(page_title="y1", layout="centered")

# RTL Support for Arabic display
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

# 3. Model Selection Logic
@st.cache_resource
def get_model():
    priorities = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-1.0-pro']
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for p in priorities:
            if p in available:
                return genai.GenerativeModel(p)
        return genai.GenerativeModel(available[0])
    except:
        return genai.GenerativeModel('gemini-1.5-flash')

model = get_model()

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
            # Building history for the API
            history = [
                {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                for m in st.session_state.messages[:-1]
            ]
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {str(e)}")
