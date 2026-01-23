import streamlit as st
import google.generativeai as genai

# 1. Page Configuration & RTL UI
st.set_page_config(page_title="y1", layout="centered")

# CSS to force Arabic-friendly layout (Right-to-Left)
st.markdown("""
    <style>
    .stMarkdown { text-align: right; }
    div[data-testid="stVerticalBlock"] { direction: rtl; }
    div[data-testid="stChatInput"] { direction: ltr; } /* Input remains LTR for better typing experience */
    </style>
    """, unsafe_allow_html=True)

st.title("y1")

# 2. Secure API Configuration
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing GOOGLE_API_KEY in secrets.")
    st.stop()

# 3. Dynamic Model Discovery (Optimized for Iraq/Regional Access)
@st.cache_resource
def get_optimized_model():
    priority_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-1.0-pro']
    available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    for model_path in priority_models:
        if model_path in available:
            return genai.GenerativeModel(model_path)
    return genai.GenerativeModel(available[0]) if available else None

chat_model = get_optimized_model()

# 4. Session State Management (Temporary Memory)
# This clears automatically when the browser tab is closed or refreshed
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display current session messages
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. Chat Interaction Logic
if prompt := st.chat_input("Ask y1..."):
    # Add user message to session
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI Response using session memory
    with st.chat_message("assistant"):
        try:
            # Format history for the API (Converting roles for Gemini compatibility)
            api_memory = [
                {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                for m in st.session_state.chat_history[:-1]
            ]
            
            chat_session = chat_model.start_chat(history=api_memory)
            response = chat_session.send_message(prompt)
            
            # Save and display response
            ai_response = response.text
            st.markdown(ai_response)
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
