
import streamlit as st
import requests
import json
from pathlib import Path


CHAT_FILE = Path("frontend/recent_chats.json")


def load_chats():
    if CHAT_FILE.exists():
        return json.loads(CHAT_FILE.read_text())
    return []


def save_chats(chats):
    CHAT_FILE.write_text(json.dumps(chats, indent=2))

def load_css():
    with open("frontend/style.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )


BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="HireMeAI",
    page_icon="🤖",
    initial_sidebar_state="expanded"
)

# Dark mode state
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_titles" not in st.session_state:
    st.session_state.chat_titles = load_chats()

# CSS
load_css()


# Sidebar
with st.sidebar:

    st.header("💬 HireMeAI")

    st.divider()

    st.subheader("Recent Chats")

    if len(st.session_state.chat_titles) == 0:
        st.caption("No recent chats")

    else:
        for title in st.session_state.chat_titles[-10:]:
            st.button(
                title,
                use_container_width=True
            )




# Main UI
st.title("HireMeAI 🤖")
st.caption("Sanjana's Personal Portfolio ")


# Show previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat input
question = st.chat_input("Ask about the candidate...")


if question:

    # Add question to recent chats
   if question not in st.session_state.chat_titles:
    st.session_state.chat_titles.append(question)
    save_chats(st.session_state.chat_titles)

    # Show user message
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)


    # Ask backend
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"question": question},
                    timeout=60
                )

                if response.status_code == 200:

                    answer = response.json()["answer"]

                    st.markdown(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                else:

                    st.error(
                        f"Backend error: {response.status_code}"
                    )


            except requests.exceptions.ConnectionError:

                st.error(
                    "Backend connect nahi ho raha. "
                    "FastAPI server check karo."
                )


            except requests.exceptions.Timeout:

                st.error(
                    "Backend response dene mein bahut time le raha hai."
                )


            except Exception as e:

                st.error(f"Error: {e}")

