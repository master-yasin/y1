import streamlit as st
import google.generativeai as genai

# 1. Page Configuration
st.set_page_config(page_title="y1", layout="centered")

# Custom CSS for RTL support
st.markdown("""
    <style>
    .stMarkdown { text-align: right; }
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
# This part will find the first available model that supports generating content
@st.cache_resource
def get_available_model():
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            # We prefer Gemini 1.5 Flash or Pro if available
            if '1.5' in m.name:
                return m.name
    return 'gemini-pro' # Fallback

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
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            output = response.text
            st.markdown(output)
            st.session_state.messages.append({"role": "assistant", "content": output})
        except Exception as e:
            st.error(f"Error: {str(e)}")
