import streamlit as st
import google.generativeai as genai

# 1. UI Setup (RTL Support)
st.set_page_config(page_title="y1", layout="centered")
st.markdown("""<style>.stMarkdown {text-align: right;} div[data-testid="stVerticalBlock"] {direction: rtl;}</style>""", unsafe_allow_html=True)
st.title("y1")

# 2. Authentication
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API Key Missing")
    st.stop()

# 3. Secure Model Selection
# Using 'gemini-pro' as it's the most compatible model across all API versions
model = genai.GenerativeModel('gemini-pro')

if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Chat Engine with Session Memory
if prompt := st.chat_input("..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Preparing history: Converting 'assistant' to 'model' for Gemini compatibility
            history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                       for m in st.session_state.messages[:-1]]
            
            # Start session and get response
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
