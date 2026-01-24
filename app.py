import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="y1", layout="centered")

if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API Key Missing")
    st.stop()

@st.cache_resource
def get_safe_model():
    try:
        # Get all models
        all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # FILTER: Avoid 2.5 because it has a 20-message limit
        safe_models = [m for m in all_models if "2.5" not in m]
        
        if safe_models:
            # Try to find 1.5 flash first, if not take the first safe one
            selected = next((m for m in safe_models if "1.5-flash" in m), safe_models[0])
            return genai.GenerativeModel(selected), selected
        else:
            # If ONLY 2.5 exists, we are forced to use it (or wait for quota reset)
            return genai.GenerativeModel(all_models[0]), all_models[0]
    except Exception as e:
        st.error(f"Discovery Error: {e}")
        return None, None

model_engine, model_name = get_safe_model()
st.info(f"System is using: {model_name}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Enter message"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                       for m in st.session_state.messages[:-1]]
            chat = model_engine.start_chat(history=history)
            response = chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {str(e)}")
