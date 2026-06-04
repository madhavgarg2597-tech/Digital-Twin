import json
from pathlib import Path

import streamlit as st

def _init_chats():
    if "chats" not in st.session_state:
        st.session_state.chats = {}
    if "active_chat_id" not in st.session_state:
        st.session_state.active_chat_id = None

def create_chat(chat_id, title="New Chat"):
    _init_chats()
    st.session_state.chats[chat_id] = {
        "title": title,
        "messages": [],
        "chat_memory": [],
    }
    st.session_state.active_chat_id = chat_id

def get_active_chat():
    _init_chats()
    cid = st.session_state.active_chat_id
    if cid and cid in st.session_state.chats:
        return st.session_state.chats[cid]
    return None

def delete_chat(chat_id):
    _init_chats()
    if chat_id in st.session_state.chats:
        del st.session_state.chats[chat_id]
    if st.session_state.active_chat_id == chat_id:
        remaining = list(st.session_state.chats.keys())
        st.session_state.active_chat_id = (
            remaining[0] if remaining else None
        )

def add_to_memory(role, content):
    chat = get_active_chat()
    if chat is None:
        return
    chat["chat_memory"].append({
        "role": role,
        "content": content
    })
    chat["chat_memory"] = chat["chat_memory"][-6:]

def get_memory():
    chat = get_active_chat()
    if chat is None:
        return ""
    history = []
    for item in chat["chat_memory"]:
        history.append(
            f"{item['role']}: {item['content']}"
        )
    return "\n".join(history)

def clear_memory():
    chat = get_active_chat()
    if chat is None:
        return
    chat["chat_memory"] = []

MEMORY_FILE = "long_term_memory.json"

def load_long_term():

    if not Path(MEMORY_FILE).exists():

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump([], f)

        return []

    with open(
        MEMORY_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)

def save_long_term(memories):

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            memories,
            f,
            indent=2,
            ensure_ascii=False
        )

def remember(memory_text):

    memories = load_long_term()

    if memory_text not in memories:

        memories.append(
            memory_text
        )

        save_long_term(
            memories
        )

def get_long_term():

    memories = load_long_term()

    return "\n".join(memories)

def clear_long_term():

    save_long_term([])