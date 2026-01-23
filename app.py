import streamlit as st
import google.generativeai as genai
import urllib.parse

# 1. Page Configuration
st.set_page_config(page_title="y1", layout="centered")

st.markdown("""
    <style>
    .stMarkdown { text-align: left; }
    </style>
    """, unsafe_allow_html=True)

st.title("y1")

# 2. API Key Configuration
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Configuration Error: GOOGLE_API_KEY not found.")
    st.stop()

# 3. Safe Model Selection
@st.cache_resource
def get_available_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except:
        return 'gemini-pro'
    return 'gemini-pro'

model_name = get_available_model()
model = genai.GenerativeModel(model_name)

# 4. Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("type") == "image":
            st.image(message["content"])
        else:
            st.markdown(message["content"])

# 5. Chat Logic
if prompt := st.chat_input("Enter your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Image Detection logic
        image_keywords = ['draw', 'paint', 'image', 'picture', 'generate', 'create']
        is_image_request = any(keyword in prompt.lower() for keyword in image_keywords)

        if is_image_request:
            try:
                with st.spinner("Processing..."):
                    encoded_prompt = urllib.parse.quote(prompt)
                    image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed=2026&nologo=true"
                    st.image(image_url)
                    st.session_state.messages.append({"role": "assistant", "content": image_url, "type": "image"})
            except Exception as e:
                st.error("Image failed")
        else:
            try:
                # Direct API call
                response = model.generate_content(prompt)
                if response:
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text, "type": "text"})
            except Exception as e:
                # Debugging info
                st.error(f"API Error: {str(e)}")
