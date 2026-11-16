import os

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

from wicketwise import AI_NAME, DOC_PATH, MODEL, build_system_prompt, load_document

load_dotenv()

st.set_page_config(page_title=AI_NAME, page_icon="🏏", layout="centered")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }

.stApp {
    background:
        radial-gradient(900px 500px at 10% -10%, rgba(99, 102, 241, 0.25), transparent 60%),
        radial-gradient(800px 500px at 100% 0%, rgba(16, 185, 129, 0.18), transparent 60%),
        #0a0d14;
    color: #e8eaf0;
}
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stBottom"] > div { background: transparent; }

.hero { text-align: center; padding: 2.2rem 0 1.2rem 0; }
.badge {
    display: inline-block;
    padding: .25rem .8rem;
    border-radius: 999px;
    font-size: .75rem;
    font-weight: 600;
    color: #a5b4fc;
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(99, 102, 241, 0.35);
    margin-bottom: .9rem;
}
.hero h1 {
    font-size: 3.2rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -1.5px;
    background: linear-gradient(90deg, #818cf8, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero p { color: #8b93a7; margin-top: .5rem; font-size: 1.02rem; }

.stButton > button {
    width: 100%;
    text-align: left;
    background: rgba(255, 255, 255, 0.04);
    color: #d6d9e3;
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 14px;
    padding: .9rem 1rem;
    font-size: .92rem;
    font-weight: 500;
    transition: all .2s ease;
}
.stButton > button:hover {
    background: rgba(99, 102, 241, 0.14);
    border-color: rgba(129, 140, 248, 0.6);
    color: #fff;
    transform: translateY(-2px);
}

[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: .9rem 1.1rem;
    backdrop-filter: blur(8px);
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(79, 70, 229, 0.12));
    border-color: rgba(129, 140, 248, 0.35);
}
[data-testid="stChatMessage"] p { color: #e8eaf0; line-height: 1.6; }

[data-testid="stChatInput"] {
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: rgba(255, 255, 255, 0.05);
}

[data-testid="stSidebar"] {
    background: rgba(10, 13, 20, 0.95);
    border-right: 1px solid rgba(255, 255, 255, 0.07);
}
.stat {
    padding: .8rem 1rem;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: .6rem;
}
.stat small { color: #8b93a7; display: block; font-size: .72rem; text-transform: uppercase; letter-spacing: .6px; }
.stat b { font-size: 1.05rem; color: #fff; }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="hero">
    <span class="badge">✨ Powered by Gemini</span>
    <h1>🏏 {AI_NAME}</h1>
    <p>Ask anything about cricket. Answers come only from my records.</p>
</div>
""",
    unsafe_allow_html=True,
)

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("GEMINI_API_KEY not found. Add it to your .env file.")
    st.stop()

if "chat" not in st.session_state:
    st.session_state.client = genai.Client(api_key=api_key)
    st.session_state.chat = st.session_state.client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(
            system_instruction=build_system_prompt(load_document(DOC_PATH)),
            temperature=0.2,
        ),
    )
    st.session_state.messages = []

asked = sum(m["role"] == "user" for m in st.session_state.messages)

with st.sidebar:
    st.markdown(f"### 🏏 {AI_NAME}")
    st.markdown(
        f'<div class="stat"><small>Model</small><b>{MODEL}</b></div>'
        f'<div class="stat"><small>Knowledge source</small><b>{DOC_PATH}</b></div>'
        f'<div class="stat"><small>Questions asked</small><b>{asked}</b></div>',
        unsafe_allow_html=True,
    )
    if st.button("🗑️ New chat"):
        st.session_state.pop("chat")
        st.rerun()

SUGGESTIONS = [
    "🏆 Who won the 1983 World Cup?",
    "🎯 How many Test wickets did Warne take?",
    "💯 How many centuries did Tendulkar score?",
    "❓ Who won the 2024 T20 World Cup?",
]

question = None

if not st.session_state.messages:
    cols = st.columns(2)
    for i, s in enumerate(SUGGESTIONS):
        if cols[i % 2].button(s, key=f"sugg{i}"):
            question = s.split(" ", 1)[1]

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="🧑" if m["role"] == "user" else "🏏"):
        st.markdown(m["content"])

typed = st.chat_input("Message WicketWise...")
question = typed or question

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🏏"):
        with st.spinner("Thinking..."):
            try:
                answer = st.session_state.chat.send_message(question).text
            except Exception as e:
                answer = f"Something went wrong ({e})"
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
