import streamlit as st
import google.generativeai as genai

# 1. Page & RTL Setup
st.set_page_config(page_title="y1", layout="centered")
st.markdown("""<style>.stMarkdown {text-align: right;} div[data-testid="stVerticalBlock"] {direction: rtl;}</style>""", unsafe_allow_html=True)
st.title("y1")

# 2. API Key
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing API Key")
    st.stop()

# 3. Dynamic Model Discovery (Specifically for regional restrictions)
@st.cache_resource
def find_best_model():
    # Priority list of models
    priorities = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-1.0-pro']
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Check if any priority model is available in your region
    for p in priorities:
        full_name = f"models/{p}"
        if full_name in available_models:
            return full_name
    
    # Fallback to the first available non-experimental model
    return available_models[0] if available_models else None

selected_model = find_best_model()

if not selected_model:
    st.error("No compatible models found in your region.")
    st.stop()

model = genai.GenerativeModel(selected_model)

# 4. Session Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Chat Engine
if prompt := st.chat_input("..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Transform history for Gemini
            history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                       for m in st.session_state.messages[:-1]]
            
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
