import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import speech_recognition as sr
import io

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

# 4. Session State for Chat History and Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Helper function for Speech-to-Text
def speech_to_text(audio_bytes):
    recognizer = sr.Recognizer()
    audio_data = io.BytesIO(audio_bytes)
    with sr.AudioFile(audio_data) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio, language='ar-SA')
    except:
        return None

# Helper function for Text-to-Speech
def text_to_speech(text):
    tts = gTTS(text=text, lang='ar')
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    return audio_fp

# Display Message History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Voice Input UI
with st.sidebar:
    st.header("Voice Menu")
    voice_input = mic_recorder(
        start_prompt="Record Voice (AR)",
        stop_prompt="Stop Recording",
        key='mic'
    )

# 6. Chat Logic (Handling both Text and Voice)
prompt = st.chat_input("Enter your message...")

if voice_input:
    text_from_voice = speech_to_text(voice_input['bytes'])
    if text_from_voice:
        prompt = text_from_voice

if prompt:
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response with Memory
    with st.chat_message("assistant"):
        try:
            # Create history list for the model to provide context/memory
            history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
            chat_session = model.start_chat(history=history)
            
            response = chat_session.send_message(prompt)
            output = response.text
            
            # Display Text
            st.markdown(output)
            
            # Play Voice Output
            audio_response = text_to_speech(output)
            st.audio(audio_response, format='audio/mp3', autoplay=True)
            
            # Save Assistant Message
            st.session_state.messages.append({"role": "assistant", "content": output})
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
