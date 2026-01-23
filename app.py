import streamlit as st
import google.generativeai as genai

# 1. Page Configuration
st.set_page_config(page_title="y1", layout="centered")

# Custom CSS for RTL support
st.markdown("""
    <style>
    .stMarkdown { text-align: right; }
    div[data-testid="stVerticalBlock"] { direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

st.title("y1")

# 2. API Key Configuration
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Configuration Error: GOOGLE_API_KEY not found.")
    st.stop()

# 3. Dynamic Model Selection
@st.cache_resource
def get_available_model():
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            if '1.5' in m.name:
                return m.name
    return 'gemini-pro'

model_name = get_available_model()
model = genai.GenerativeModel(model_name)

# 4. Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Message History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Chat Logic
if prompt := st.chat_input("Enter your message..."):
    # Append User Message to UI State
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Constructing correct history format for Gemini's ChatSession
            # Gemini expects 'user' and 'model' roles only
            history_for_api = []
            for m in st.session_state.messages[:-1]:
                role = "user" if m["role"] == "user" else "model"
                history_for_api.append({"role": role, "parts": [m["content"]]})
            
            # Initialize Chat Session with memory
            chat_session = model.start_chat(history=history_for_api)
            
            # Send message and get response
            response = chat_session.send_message(prompt)
            output = response.text
            
            # Display response and save to state
            st.markdown(output)
            st.session_state.messages.append({"role": "assistant", "content": output})
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
