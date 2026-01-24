import streamlit as st
import google.generativeai as genai

# 1. Page Config
st.set_page_config(page_title="y1", layout="centered")

# 2. API Config
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API Key Missing")
    st.stop()

# 3. THE INSPECTOR: Discovering what Google actually allows for you
@st.cache_resource
def discover_and_initialize():
    try:
        # Get all models that support generating content
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Display the list for one time to understand the issue
        if available_models:
            # We will pick the first one that is NOT experimental if possible
            # Otherwise, pick the very first one available
            selected = None
            for name in available_models:
                if "flash" in name.lower() and "vision" not in name.lower():
                    selected = name
                    break
            
            if not selected:
                selected = available_models[0]
                
            return genai.GenerativeModel(selected), selected
        else:
            return None, None
    except Exception as e:
        st.error(f"Discovery Error: {e}")
        return None, None

model_engine, model_name = discover_and_initialize()

# Show the active model name to the user for once
if model_name:
    st.info(f"Active System Model: {model_name}")
else:
    st.error("No models found. Please check your API Key permissions.")
    st.stop()

# 4. UI & Session Memory
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
            chat = model_engine.start_chat(history=history)
            response = chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Chat Error: {str(e)}")
